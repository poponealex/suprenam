__import__("sys").path.extend(["..", "."])
import logging, re, subprocess, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
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


def start_logging():
    path = Path.cwd() / "logs"
    if not path.exists():
        path.mkdir()
    log_name = f"log_{str(datetime.now()).replace(' ', '_')}.log"
    logging.basicConfig(
        filename=f"{path / log_name}", encoding="utf-8", level=logging.DEBUG, format=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT
    )
    logging.info("Logging has started.")


def create_temporary_file(paths: Population) -> Path:
    temp_file = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
    logging.info(f"Creating temporary file: {temp_file}")
    temp_file.write_text("\n".join(f"#{inode}# {path.name}" for inode, path in paths.items()))
    return temp_file


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
        if not name:
            continue
        try:
            inode, new_name = strip_name(name.strip())[0]
        except:
            raise ValueError(f"Error parsing the new names: {name}")
        if "/" in new_name:
            raise ValueError(f"< {new_name} > : Illegal character '/'.")
        file_path = file_system.as_population.pop(inode, None)
        if not file_path:
            raise ValueError(f"Illegal file path or trying to rename the same file twice+: {name}")
        destination_path = Path(file_path.parent / new_name)
        if destination_path in destinations:
            raise ValueError(f"Trying to rename two siblings with the same name ({file_path} -> {destination_path}).")
        if destination_path in file_system.as_set and destination_path not in population_paths:
            raise ValueError(f"Trying to rename a file with the name of an existing file ({file_path} -> {destination_path}).")
        destinations.add(destination_path)
        if file_path.name != new_name:
            logging.info(f"Clause added: {file_path} -> {new_name}")
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
    logging.info(f"Sorted clauses ready for renaming:\n{result}")
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


def renamer(levels: Levels, file_system: FileSystem, completed_renames: list = []):
    for level in levels:
        edges = create_edges(level, file_system)
        logging.info(f"Create edges for {level}:\n{edges}")
        for edge in edges.temporary_edges:
            file_system.rename(edge.original_path, edge.destination_path)
            logging.info(f"RENAME: {edge.original_path} -> {edge.destination_path}")
            completed_renames.append(edge)
        for edge in edges.final_edges:
            file_system.rename(edge.original_path, edge.destination_path)
            logging.info(f"RENAME: {edge.original_path} -> {edge.destination_path}")
            completed_renames.append(edge)
        for clause in level:
            print_rename(str(clause.path), str(Path(clause.path.parent / clause.new_name)))


def unrenamer(file_system: FileSystem, edges: list):
    for edge in edges[::-1]:
        file_system.rename(edge.destination_path, edge.original_path)
        logging.info(f"UNRENAME: {edge.destination_path} -> {edge.original_path}")


def main():
    start_logging()
    args = cli_arguments()
    if not (args.paths or args.file):
        logging.warning("No path provided.")
        return print_warning("You didn't provide any path.")
    paths = []
    if args.paths:
        paths += args.paths
    if args.file:
        paths += Path(args.file).read_text().split("\n")
    fs = FileSystem(paths)
    logging.info(f"Create FileSystem:\n{paths}")
    temporary_file = create_temporary_file(fs.as_population)
    subprocess.run(["open", temporary_file]).check_returncode()
    if not messagebox.askokcancel("Confirm changes", "Rename the files?"):
        logging.info("Renaming aborted by user.")
        return print_warning("Aborting, no changes were made.")
    new_names = parse_new_names(fs, temporary_file.read_text().split("\n"))
    if new_names:
        completed_renames = []
        try:
            renamer(sort_clauses(new_names), fs, completed_renames)
        except Exception as e:
            unrenamer(fs, completed_renames)
            raise e
    return print_success("\nBYE!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(e)
        print_fail(str(e))
    logging.info("END OF PROGRAM")
    sys.exit(0)
