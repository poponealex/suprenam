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
    file_system = FileSystem([])
    renamings = secure_clauses(file_system, edit_paths(paths))
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


def edit_paths(
    paths: List[Path],
    get_inode=lambda path: path.stat().st_ino,
    create_temporary_file=lambda paths: create_temporary_file(paths),
    get_edition_handler=lambda file: file.read_text(),
    edit=lambda editor: subprocess.run(editor, check=True),
    handler=lambda file: get_editor_command_name(platform().split("-")[0]) + [str(file)],
):
    """
    Create the user interaface and parse the renamings, can be parameterized to work with a pure FileSystem.

    Args:
        paths: List of Paths to rename.
        get_inode: function called to get the inode.
        create_temporary_file: function called to create a temporary file populated with the paths to rename.
        get_edition_handler: function called to read the content of the temporary file.
        edit: function called to run the handler.
        handler: the argument used by the edit function.

    Returns:
        A list of Clause with the effective renamings.
    """
    population = {get_inode(path): path for path in paths}
    temp_file = create_temporary_file(population.values())
    edit(handler(temp_file))
    text = get_edition_handler(temp_file)
    return parse_text(text, population)


def get_text(paths: List[Path], get_inode=lambda path: path.stat().st_ino) -> str:
    """
    Get the text to output to the user's interface.

    Args:
        paths: List of Paths to rename.

    Returns:
        A string formated as follow:
            Parent Directory path
            inode   file name
    """
    sorted_paths = sorted(paths, key=lambda path: len(path.parts))
    result = []
    for _, current_paths in groupby(sorted_paths, key=lambda path: len(path.parts)):
        current_paths = list(current_paths)
        result += [f"{current_paths[0].resolve().parent}\n"]
        result += [f"{get_inode(path)}\t{path.name}" for path in current_paths] + ["\n"]
    return "\n".join(result)[:-1]


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


def parse_text(
    text: str,
    population: dict,
    find_all=re.compile(r"(\d+)\t(.+)").findall,
) -> List[Clause]:
    """
    Parse the renamings' text.

    Args:
        temp_file: The temporary file's Path.
        population: dict containing each path (value) with its inode (key).
        match_renaming: Regular expression to match a line containing a renaming.

    Returns:
        A list of Clause (path, new_name).
    """
    result = []
    for (inode, new_name) in find_all(text):
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
