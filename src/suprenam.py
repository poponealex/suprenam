import re
import subprocess, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from itertools import groupby
from pathlib import Path
from platform import platform
from tempfile import NamedTemporaryFile
from typing import List


from src.default_editor import get_editor_command_name
from src.file_system import FileSystem
from src.goodies import *
from src.renamings import perform_renamings, undo_renamings, set_logger
from src.secure_clauses import secure_clauses
from src.user_types import Clause


LOG_DIR = Path.cwd() / ".suprenam"
LOG_NAME = "previous_session.log"


def main():
    args = cli_arguments()
    paths = []
    if args.undo:
        return undo_renamings(LOG_DIR / LOG_NAME)
    if args.paths:
        paths += [*map(lambda x: Path(x), args.paths)]
    if args.file:
        paths += [Path(path) for path in Path(args.file).read_text().split("\n") if path]
    if not paths:
        return print_warning("No paths were provided.")
    create_log()
    file_system = FileSystem()
    population = {path.stat().st_ino: path for path in paths}
    temp_file = create_temporary_file(population.values())
    os = platform().split("-")[0]
    subprocess.run(get_editor_command_name(os) + [str(temp_file)], check=True)
    renamings = secure_clauses(file_system, parse_temporary_file(temp_file, population))
    return perform_renamings(renamings)


def cli_arguments():
    """
    CLI argument parser.

    Returns:
        `parser.parse_args()` dict containing the parsed arguments.
    """
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        usage=f"\n{WARNING}suprenam.py [-p paths] [-f file] [-h help]{RESET}",
        description=f"{OK}\nFILE RENAMER{RESET}",
    )

    parser.add_argument(
        "-p",
        "--paths",
        nargs="+",
        help=f"{OK}The paths you want to rename.{RESET}",
        action="store",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=f"{OK}Parse paths stored in a file (newline separated).{RESET}",
        action="store",
    )

    parser.add_argument(
        "-u",
        "--undo",
        help=f"{OK}Undo completed renamings from the previous session.{RESET}",
        action="store",
    )

    return parser.parse_args()


def get_text(paths: List[Path]) -> str:
    """
    Get the text to output to the user's interface.

    Args:
        paths: List of paths to rename.

    Returns:
        A string formated as follow:
            Parent Directory path
            inode   file name
    """
    sorted_paths = sorted(paths, key=lambda path: len(path.parts), reverse=True)
    result = ""
    for _, current_paths in groupby(sorted_paths, key=lambda path: len(path.parts)):
        current_paths = list(current_paths)
        result += f"{current_paths[0].resolve().parent}\n\n"
        result += "\n".join(f"{path.stat().st_ino}\t{path.name}" for path in current_paths)
        result += "\n"
    return result


def create_temporary_file(paths: List[Path]) -> Path:
    """
    Create a temporary file populated with the names of the files to rename.

    Args:
        paths: List of paths to rename.

    Returns:
        The temporary file's Path.
    """
    temp_file = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
    temp_file.write_text(get_text(paths))
    return temp_file


def parse_temporary_file(
    temp_file: Path,
    population: dict,
    find_all=re.compile(r"(\d+)\t(.+)").findall,
) -> List[Clause]:
    """
    Parse the temporary file to collect the renamings.

    Args:
        temp_file: The temporary file's Path.
        population: dict containing each path (value) with its inode (key).
        match_renaming: Regular expression to match a line containing a renaming.

    Returns:
        A list of Clause (path, new_name).

    Raises:
        IllegalCharacter Error: An error is raised if the user enter a renaming with the '/' character.
        IllegalInode Error : An error is raised if an inode is modified.
    """
    result = []
    for (inode, new_name) in find_all(temp_file.read_text()):
        path = population.get(int(inode))
        if path:
            result += [Clause(path, new_name)]
    return result


def create_log():
    if not LOG_DIR.exists():
        LOG_DIR.mkdir()
    return set_logger(LOG_DIR / LOG_NAME)


if __name__ == "__main__":
    sys.exit(main())
