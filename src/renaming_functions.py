from pathlib import Path
from typing import NamedTuple
from random import choice
from string import ascii_lowercase
from path_siblings import get_path_siblings
from create_fhs import create_fhs


class Clause(NamedTuple):
    path: Path
    new_name: str


class Direction(NamedTuple):
    original_path: Path
    destination_path: Path


def create_temporary_filename(length: int = 15):
    return "".join(choice(ascii_lowercase) for _ in range(length))


def sort_clauses(clauses: list[Clause]) -> list[list[Clause]]:
    result = []
    paths_lengths = sorted([(clause, len(str(clause.path).split("/"))) for clause in clauses], key=lambda x: x[1])
    acc = [paths_lengths[-1][0]]
    for i in range(len(paths_lengths) - 2, -1, -1):
        if paths_lengths[i][1] == paths_lengths[i + 1][1]:
            acc.append(paths_lengths[i][0])
        else:
            result.append(acc)
            acc = [paths_lengths[i][0]]
    result.append(acc)
    return result


def create_paths_directions(clauses: list[Clause], arborescence: set[Path]) -> tuple[list[Direction], list[Direction]]:
    final_directions = []
    temporary_directions = []
    acc = set()
    for clause in clauses:
        if clause.path.name == clause.new_name:
            final_directions.append(Direction(clause.path, clause.path))
            continue
        destination_path = Path(f"{clause.path.parent}/{clause.new_name}")
        acc.add(destination_path)
        if destination_path not in arborescence:
            final_directions.append(Direction(clause.path, destination_path))
        elif destination_path in arborescence:
            while (temp_path := Path(f"{clause.path.parent}/{create_temporary_filename()}")) in acc or temp_path in arborescence:
                continue
            acc.add(temp_path)
            temporary_directions.append(Direction(clause.path, temp_path))
            final_directions.append(Direction(temp_path, destination_path))
    return (temporary_directions, final_directions)


def renamer(clauses_list: list[list[Clause]], arborescence: set[Path]):
    for clauses in clauses_list:
        (temporary_directions, final_directions) = create_paths_directions(clauses, arborescence)
        for direction in temporary_directions:
            direction.original_path.rename(direction.destination_path)
        for direction in final_directions:
            direction.original_path.rename(direction.destination_path)

# create_fhs()
# arborescence = get_path_siblings(set([Path("FHS"), Path("FHS/var/tmp"), Path("FHS/var/empty"), Path("FHS/var"), Path("FHS/etc/X11"), Path("FHS/etc/skell"), Path("FHS/etc/X11/applnk")]))
# clauses = sort_clauses([Clause(Path("FHS"), "FHS_RENAMED"), Clause(Path("FHS/var/tmp"), "empty"), Clause(Path("FHS/var/empty"), "tmp"), Clause(Path("FHS/var"), "bar"), Clause(Path("FHS/etc/X11"), "X12"), Clause(Path("FHS/etc/skel"), "well"), Clause(Path("FHS/etc/X11/applnk"), "serverconfig"), Clause(Path("FHS/etc/X11/serverconfig"), "applnk")])
# renamer(clauses, arborescence)
