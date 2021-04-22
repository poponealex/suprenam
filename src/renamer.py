from pathlib import Path
from typing import List, Iterable
from collections import Counter

from src.file_system import FileSystem


def check_and_complete(paths: Iterable[Path]):
    """Check that the given concrete paths exist, and add the other children of their parents."""
    result = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError
        result.update(path.parent.glob("*"))
    return result


def sorted_by_level(clauses):
    return sorted(clauses.items(), key=lambda item: len(item[0].parts), reverse=True)


def redundant_targets(clauses):
    bag = Counter(path.with_name(new_name) for (path, new_name) in clauses.items())
    duplicates = []
    for (new_path, count) in bag.most_common():
        if count == 1:
            break
        duplicates.append(new_path)
    return duplicates


def outer_name_clashes(file_system, clauses):
    clashes = []
    for (path, new_name) in clauses.items():
        new_path = path.with_name(new_name)
        if new_path in file_system and new_path not in clauses:
            clashes.append(new_path)
    return clashes


def rename(clause_list, file_system=None):
    clauses = {}
    for (path, new_name) in clause_list:
        if path in clauses:
            if clauses[path] == new_name:
                continue  # skip null renaming
            else:
                return  # TODO: update the error report
        clauses[path] = new_name

    if redundant_targets(clauses):
        return  # TODO: update the error report

    if file_system is None:
        file_system = FileSystem(check_and_complete(clauses.keys()))

    if outer_name_clashes(file_system, clauses):
        return  # TODO: update the error report

    clauses = sorted_by_level(clauses)
    i = 0
    while i < len(clauses):  # `clauses` sequence may grow
        (path, new_name) = clauses[i]
        new_path = path.with_name(new_name)
        if new_path in file_system:
            new_path = file_system.non_existing_sibling(path)
            clauses.append((new_path, new_name))
        file_system.rename(path, new_path)
        i += 1
