from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple, NewType, Dict

from src.file_system import FileSystem

Name = NewType("Name", str)

def secure_clauses(
    file_system: FileSystem,
    clauses: List[Tuple[Path, Name]],
) -> List[Tuple[Path, Name]]:
    """Construct a "safe" version of the given renaming clauses and update the file system.

    The resulting sequence is a reordered copy of the given clauses, with potentially the
    insertion of intermediate renamings, in such a way that they can be executed sequentially in
    the concrete file system without any collisions or other adverse effect.

    Args:
        clauses (List[Tuple[Path, Name]]): A collection of renaming clauses of the form `(path,
        new_name)` in no particular order.
        file_system (FileSystem): Either a nonempty list of paths
    
    Raises:
        SourceHasMultipleTargetsError: when two distinct renaming targets are specified for the same source.
        TargetHasMultipleSourcesError: when two distinct sources have the same renaming target, or when a
            renaming target already exists and has no specified renaming.
        FileNotFound: when a source does not exist in the file system.

    Side Effect:
        The underlying (pure) file system is brought to the expected final state (i.e., as if
        all the renamings would have been executed).

    Returns:
        List[Tuple[Path, Name]]: A "safe" version of the given renaming clauses.
    """
    clause_dict = dict_of_clauses(clauses)
    file_system.update_with_source_paths(clause_dict.keys())
    check_injectivity(file_system, clause_dict)
    clauses = sorted_by_level(clause_dict)
    i = 0
    while i < len(clauses):  # `clauses` sequence may grow
        (path, new_name) = clauses[i]
        new_path = path.with_name(new_name)
        if new_path in file_system:
            new_path = file_system.non_existing_sibling(path)
            clauses[i] = (path, Name(new_path.name))
            clauses.append((new_path, new_name))
        file_system.rename(path, new_path)
        i += 1
    return clauses


class SourceHasMultipleTargetsError(Exception):
    ...


def dict_of_clauses(clauses: Iterable[Tuple[Path, Name]]) -> Dict[Path, Name]:
    """Make a dictionary from the given clauses.

    The result is silently deduplicated. During its construction, a `SourceHasMultipleTargetsError` is raised
    iff there exists at least one couple of clauses `(path, new_name_1)` and `(path, new_name_2)`
    with `new_name_1 != new_name_2`.

    Args:
        clauses (List[Tuple[Path, Name]]): A list of couples of the form `(path, new_name)`.

    Raises:
        SourceHasMultipleTargetsError: Two distinct new names are specified for the same path.

    Returns:
        Dict[Path, Name]: A dictionary associating paths to new names.
    """
    result: Dict[Path, Name] = {}
    for (path, new_name) in clauses:
        if path in result and result[path] != new_name:
            raise SourceHasMultipleTargetsError(path)
        result[path] = new_name
    return result


class TargetHasMultipleSourcesError(Exception):
    ...


def check_injectivity(file_system: FileSystem, clauses: Dict[Path, Name]):
    """Check that no resulting path has more than one antecedent.

    This function detects the following problems:

    1. There are two sibling nodes being renamed onto the same target path.
    2. There is a node being renamed onto a target path which already exists in the
       file system is not renamed itself (i.e., is not the source of any clause).

    Args:
        clauses (Dict[Path, Name]): A dictionary associating paths to new names.

    Raises:
        TargetHasMultipleSourcesError: A resulting path has two distinct antecedents.
    """
    already_seen = set()
    for (path, new_name) in clauses.items():
        new_path = path.with_name(new_name)
        if new_path in already_seen or (new_path in file_system and new_path not in clauses):
            raise TargetHasMultipleSourcesError(new_path)
        already_seen.add(new_path)


def sorted_by_level(clauses: Dict[Path, Name]):
    """Order the items of a clause dictionary with the most nested first."""
    return sorted(clauses.items(), key=lambda item: len(item[0].parts), reverse=True)
