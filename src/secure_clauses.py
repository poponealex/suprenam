from itertools import groupby
from typing import Iterable, List, Tuple

from src.file_system import FileSystem
from src.user_errors import DuplicatedClauseError, SeveralSourcesError, SeveralTargetsError
from src.user_types import Arc, Clause, ClauseMap, Name


def secure_clauses(file_system: FileSystem, clauses: List[Clause]) -> List[Arc]:
    """Construct a "safe" version of the given renaming clauses and update the file system.

    The resulting sequence is a reordered copy of the given clauses, with potentially the
    insertion of intermediate renamings, in such a way that they can be executed sequentially in
    the concrete file system without any collision or other adverse effect.

    Args:
        clauses (List[Clause]): A collection of renaming clauses of the form `(path, new_name)`
            in no particular order.
        file_system (FileSystem): A file system constructed either with an empty or nonempty list
            of paths:
            - empty: the arborescence will be populated by calling `update_with_source_paths()`
                with a list of source paths: this method will add not only the given paths, but
                their actual siblings too.
            - nonempty: used with a prepopulated test file system, like `test/fhs.txt`.

    Raises:
        SeveralTargetsError: when two distinct renaming targets are specified for the same source.
        SeveralSourcesError: when two distinct sources have the same renaming target, or when a
            renaming target already exists and has no specified renaming.
        FileNotFound: when a source does not exist in the file system.

    Side Effect:
        The underlying (pure) file system is brought to the expected final state (i.e., as if
        all the renamings would have been executed).

    Returns:
        List[Arc]: A "safe" version of the given renaming clauses, presented as a list of
            source and target paths.
    """
    clause_dict = dict_of_clauses(clauses)
    try:
        file_system.update_with_source_paths(clause_dict.keys())
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: '{e}'.")
    check_injectivity(file_system, clause_dict)
    clauses_by_levels = sorted_by_level(clause_dict)
    safe_clauses = []
    for (level, clauses) in clauses_by_levels:
        i = 0
        while i < len(clauses):  # `clauses` sequence may grow
            (path, new_name) = clauses[i]
            new_path = path.with_name(new_name)
            if new_path in file_system:
                new_path = file_system.non_existing_sibling(path)
                clauses[i] = Clause(path, Name(new_path.name))
                clauses.append(Clause(new_path, new_name))
            file_system.rename(path, new_path)
            i += 1
        safe_clauses.extend(clauses)
    return [Arc(path, path.parent / new_name) for (path, new_name) in safe_clauses]


def dict_of_clauses(clauses: Iterable[Clause]) -> ClauseMap:
    """Make a dictionary from the given clauses.

    During its construction, raise an error iff there exists at least one couple of clauses
    `(path, new_name_1)` and `(path, new_name_2)` (SeveralTargetsError if the new names are
    distinct, and DuplicatedClauseError otherwise).

    Args:
        clauses (List[Clause]): A list of couples of the form `(path, new_name)`.

    Raises:
        SeveralTargetsError: Two distinct new names are specified for the same path.
        DuplicatedClauseError: The same name is specified as least twice for the same path.

    Returns:
        ClauseMap: A dictionary associating paths to new names.
    """
    result: ClauseMap = {}
    for (path, new_name) in clauses:
        if path in result:
            if result[path] == new_name:
                raise DuplicatedClauseError(f"The clause '{path}' -> '{new_name}' is given twice.")
            else:
                raise SeveralTargetsError(
                    f"Two distinct renaming targets for '{path}': "
                    f"'{result[path]}' and '{new_name}'."
                )
        result[path] = new_name
    return result


def check_injectivity(file_system: FileSystem, clauses: ClauseMap):
    """Check that no resulting path has more than one antecedent.

    This function detects the following problems:

    1. There are two sibling nodes being renamed onto the same target path.
    2. There is a node being renamed onto a target path which already exists in the
       file system without being itself renamed (i.e., not the source of any clause).

    Args:
        clauses (ClauseMap): A dictionary associating paths to new names.

    Raises:
        SeveralSourcesError: A resulting path has two distinct antecedents.
    """
    already_seen = set()
    for (path, new_name) in clauses.items():
        new_path = path.with_name(new_name)
        if new_path in already_seen or (new_path in file_system and new_path not in clauses):
            raise SeveralSourcesError(f"At least two distinct sources for '{new_path}'.")
        already_seen.add(new_path)


def sorted_by_level(clauses: ClauseMap) -> List[Tuple[int, List[Clause]]]:
    """Order and group the items of a clause dictionary with the most nested first."""
    items = (Clause(*item) for item in clauses.items())  # make mypy happy
    sorted_clauses = sorted(items, key=lambda clause: len(clause.path.parts), reverse=True)
    grouped_clauses = groupby(sorted_clauses, key=lambda clause: len(clause.path.parts))
    return [(level, list(clauses)) for (level, clauses) in grouped_clauses]
