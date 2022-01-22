__import__("sys").path.extend(["..", "."])
import logging, re, subprocess, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from itertools import count, groupby
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
            raise ValueError(f"Error parsing the new name: {name}")
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


def level_of_path(clause: Clause):
    return len(clause.path.parts)


def sort_clauses(clauses: List[Clause]) -> Levels:
    clauses = sorted(clauses, key=level_of_path, reverse=True)
    result = [list(group) for (level, group) in groupby(clauses, key=level_of_path)]
    logging.info(f"Sorted clauses ready for renaming:\n{result}")
    return result


def renamer(levels: Levels, file_system: FileSystem, completed_renames: List = []):
    for level in levels:
        temporary_clauses = []
        for clause in level:
            destination_path = clause.path.with_name(clause.new_name) 
            if destination_path not in file_system.as_set:
                file_system.rename(clause.path, destination_path)
                logging.info(f"RENAME: {clause.path} -> {destination_path}")
                completed_renames.append(Edge(clause.path, destination_path))
            else:
                temp_path = file_system.uncollide(clause.path)
                file_system.rename(clause.path, temp_path)
                completed_renames.append(Edge(clause.path, temp_path))
                logging.info(f"RENAME: {clause.path} -> {temp_path}")
                temporary_clauses.append(Edge(temp_path, destination_path))
        for clause in temporary_clauses:
            file_system.rename(clause.original_path, clause.destination_path)
            completed_renames.append(Edge(clause.original_path, clause.destination_path))
            logging.info(f"RENAME: {clause.original_path} -> {clause.destination_path}")


def unrenamer(file_system: FileSystem, edges: List[Edge]):
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
        return print_warning("\nAborting, no changes were made. Bye!\n")
    new_names = parse_new_names(fs, temporary_file.read_text().split("\n"))
    if not new_names:
        return print_warning("\nYou didn't make any modication, no changes were made. Bye!\n")
    completed_renames = []
    try:
        renamer(sort_clauses(new_names), fs, completed_renames)
    except Exception as e:
        unrenamer(fs, completed_renames)
        raise e
    return print_success("\nAll good! BYE!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(e)
        print_fail(str(e))
    logging.info("END OF PROGRAM")
    sys.exit(0)
