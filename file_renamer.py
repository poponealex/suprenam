import re, sys, os
from pathlib import Path, PurePath
from typing import NamedTuple, Union, Set, Generator, Callable
from itertools import count
from tempfile import NamedTemporaryFile
from tkinter import messagebox


class Color:
    FAIL = "\033[1;91m"
    INFO = "\033[1;94m"
    TITLE = "\033[1;96m"
    END = "\033[0m"


class Clause(NamedTuple):
    path: Union[Path, PurePath]
    new_name: str


class Edge(NamedTuple):
    original_path: Union[Path, PurePath]
    destination_path: Union[Path, PurePath]


class Edges(NamedTuple):
    temporary_edges: list[Edge]
    final_edges: list[Edge]


Population = dict[str, Path]

Arborescence = set[Union[Path, PurePath]]

Clauses = list[list[Clause]]


def confirm_with_dialog() -> bool:
    return messagebox.askokcancel("Confirm changes", "Rename the files?")


def get_siblings(paths: Arborescence) -> Generator:
    for path in paths:
        yield from Path(path.parent).glob("*")


def parse_file_paths() -> Population:
    """Raises an error if an invalid path is provided."""
    if len(sys.argv) < 2:
        raise ValueError("No path was provided.")
    population = {}
    for x in sys.argv[1:]:
        if not Path(x).exists():
            raise ValueError(f"< {x} > is not a valid path.")
        population[str(Path(x).stat().st_ino)] = Path(x)
    return population


def create_temporary_file(paths: Population) -> Path:
    temp_file = NamedTemporaryFile(mode="w+", delete=False)
    Path(temp_file.name).write_text("\n".join(f"#{inode}# {path.name}" for inode, path in paths.items()))
    return Path(temp_file.name)


def parse_new_names(
    population: Population,
    arborescence: Arborescence,
    temp_file: Path,
    strip_line: Callable = re.compile(r"#(\d+)#[ ]*([\w\W]+)").findall,
) -> list[Clause]:
    result = []
    population_paths = set(population.values())
    destinations = set()
    for line in temp_file.read_text().split("\n"):
        inode, new_name = strip_line(line.strip())[0]
        file_path = population.pop(inode, None)
        if not file_path:
            raise ValueError("Illegal file path.")
        destination_path = Path(file_path.parent / new_name)
        if destination_path in destinations:
            raise ValueError("Trying to rename two siblings with the same name.")
        if destination_path in arborescence and destination_path not in population_paths:
            raise ValueError("Trying to rename a file with the name of an existing file.")
        destinations.add(destination_path)
        result.append(Clause(file_path, new_name))
    return result


def create_temporary_filename(
    file_name: str,
    arborescence: Arborescence,
    aux_arborescence: Arborescence = set(),
):
    for i in count():
        result = f"{i}{hash(file_name)}"
        if result not in arborescence and result not in aux_arborescence:
            return result


def sort_clauses(clauses: list[Clause]) -> Clauses:
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


def create_edges(clauses: list[Clause], arborescence: Arborescence) -> Edges:
    final_edges = []
    temporary_edges = []
    acc = set()
    for clause in clauses:
        if clause.path.name == clause.new_name:
            continue
        destination_path = Path(f"{clause.path.parent}/{clause.new_name}")
        acc.add(destination_path)
        temp_path = Path(f"{clause.path.parent}/{create_temporary_filename(clause.path.name, arborescence, acc)}")
        acc.add(temp_path)
        temporary_edges.append(Edge(clause.path, temp_path))
        final_edges.append(Edge(temp_path, destination_path))
    return Edges(temporary_edges, final_edges)


def renamer(clauses_list: Clauses, arborescence: Arborescence):
    for clauses in clauses_list:
        edges = create_edges(clauses, arborescence)
        for edge in edges.temporary_edges:
            edge.original_path.rename(edge.destination_path)
        for edge in edges.final_edges:
            edge.original_path.rename(edge.destination_path)
        for clause in clauses:
            print(
                f"{Color.TITLE}{str(clause.path)}{Color.INFO} renamed as {Color.TITLE}{str(Path(clause.path.parent / clause.new_name))}{Color.END}"
            )


def main():
    population = parse_file_paths()
    arborescence = {path for path in get_siblings(population.values())}
    temporary_file = create_temporary_file(population)
    os.system(f"open {temporary_file}")
    if not confirm_with_dialog():
        return print(f"{Color.FAIL}Aborting, no changes were made.{Color.END}")
    clauses = sort_clauses(parse_new_names(population, arborescence, temporary_file))
    renamer(clauses, arborescence)
    os.system(f"rm {temporary_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Color.FAIL}{e}{Color.END}", file=sys.stderr)
    sys.exit()
