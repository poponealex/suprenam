__import__("sys").path.extend(["..", "."])
import os, re, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from itertools import count
from pathlib import Path, PurePath
from src.file_system import FileSystem
from src.goodies import *
from tempfile import NamedTemporaryFile
from tkinter import messagebox
from typing import Callable, Dict, Generator, List, NamedTuple, Union


################## TYPES ##################

class Clause(NamedTuple):
    path: Union[Path, PurePath]
    new_name: str


class Edge(NamedTuple):
    original_path: Union[Path, PurePath]
    destination_path: Union[Path, PurePath]


class Edges(NamedTuple):
    temporary_edges: List[Edge]
    final_edges: List[Edge]


Population = Dict[str, Path]


Levels = List[List[Clause]]

###########################################


def cli_arguments():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        usage=f"\n{WARNING}file_renamer.py [-p paths] [-f file] [-h help]{RESET}",
        description=f"{INFO}\nFILE RENAMER{RESET}",
    )

    parser.add_argument(
        "-p",
        "--paths",
        nargs="+",
        help=f"{INFO}The paths you want to rename.{RESET}",
        action="store",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=f"{INFO}Parse paths stored in a file (newline separated).{RESET}",
        action="store",
    )

    return parser.parse_args()


def create_temporary_file(paths: Population) -> Path:
    temp_file = NamedTemporaryFile(mode="w+", delete=False)
    Path(temp_file.name).write_text("\n".join(f"#{inode}# {path.name}" for inode, path in paths.items()))
    return Path(temp_file.name)


def parse_new_names(
    file_system: FileSystem,
    new_names: List,
    strip_name: Callable = re.compile(r"#(\d+)#[ ]*([\w\W]+)").findall,
) -> List[Clause]:
    """new_names is a list of strings in the format: #inode# new_name"""

    result = []
    population_paths = set(file_system.as_population.values())
    destinations = set()
    for name in new_names:
        try:
            inode, new_name = strip_name(name.strip())[0]
        except:
            continue
        if "/" in new_name:
            raise ValueError(f"< {new_name} > : Illegal character '/'.")
        file_path = file_system.as_population.pop(inode, None)
        if not file_path:
            raise ValueError("Illegal file path or trying to rename the same file twice+.")
        destination_path = Path(file_path.parent / new_name)
        if destination_path in destinations:
            raise ValueError(f"Trying to rename two siblings with the same name ({file_path} -> {destination_path}).")
        if destination_path in file_system.as_set and destination_path not in population_paths:
            raise ValueError(f"Trying to rename a file with the name of an existing file ({file_path} -> {destination_path}).")
        destinations.add(destination_path)
        if file_path.name != new_name:
            result.append(Clause(file_path, new_name))
    return result


def sort_clauses(clauses: List[Clause]) -> Levels:
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


def create_edges(clauses: List[Clause], file_system: FileSystem) -> Edges:
    final_edges = []
    temporary_edges = []
    for clause in clauses:
        destination_path = Path(clause.path.parent / clause.new_name)
        if destination_path not in file_system.as_set:
            final_edges.append(Edge(clause.path, destination_path))
        else:
            temp_path = file_system.uncollide(clause.path)
            temporary_edges.append(Edge(clause.path, temp_path))
            final_edges.append(Edge(temp_path, destination_path))
    return Edges(temporary_edges, final_edges)


def renamer(levels: Levels, file_system: FileSystem):
    for level in levels:
        edges = create_edges(level, file_system)
        for edge in edges.temporary_edges:
            file_system.rename(edge.original_path, edge.destination_path)
        for edge in edges.final_edges:
            file_system.rename(edge.original_path, edge.destination_path)
        for clause in level:
            print_rename(clause.path, Path(clause.path.parent / clause.new_name))


def main():
    args = cli_arguments()
    if args.paths:
        fs = FileSystem(args.paths)
    elif args.file:
        fs = FileSystem(Path(args.file).read_text().split("\n"))
    else:
        return print_warning("You didn't provide any path.")
    temporary_file = create_temporary_file(fs.as_population)
    os.system(f"open {temporary_file}")
    if not messagebox.askokcancel("Confirm changes", "Rename the files?"):
        return print_warning("Aborting, no changes were made.")
    new_names = parse_new_names(fs, temporary_file.read_text().split("\n"))
    if new_names:
        renamer(sort_clauses(new_names), fs)
    return os.system(f"rm {temporary_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_fail(e)
    sys.exit(0)
