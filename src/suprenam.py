import subprocess
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

sys.path[0:0] = ["."]

from src.file_system import FileSystem
from src.get_editable_text import get_editable_text
from src.get_editor_command import get_editor_command
from src.printer import print_
from src.parse_edited_text import parse_edited_text
from src.paths_to_inodes_paths import paths_to_inodes_paths
from src.renamings import Renamer
from src.secure_clauses import secure_clauses
from src.user_errors import *
from src.user_types import EditedText


def main():
    args = cli_arguments()

    if args.undo:
        renamer = Renamer()
        try:
            renamer.undo_renamings()
        except RecoverableRenamingError:
            try:
                renamer.rollback_renamings()
                print_.no_renamings()
            except: # Unknow error during rollback.
                print_.fail("Rollback failed.")
        except: # Unknown problem with the log file, e.g. not found
            print_.fail("Undo failed.")
        return print_.flush_buffer_and_exit()

    # Construct the list of items to rename.
    paths = []
    if args.paths:  # a list of items to rename was provided
        paths.extend(map(Path, args.paths))
    if args.file:  # a file containing the paths to rename was provided
        paths.extend(Path(path) for path in Path(args.file).read_text().split("\n") if path)
    if not paths:
        return print_.no_renamings("Please provide at least one file to rename.")

    run_on_path_list(paths)
    return print_.flush_buffer_and_exit()


def run_on_path_list(paths: List[Path]):

    # Create a mapping from inodes to paths.
    try:
        inodes_paths = paths_to_inodes_paths(paths)
    except FileNotFoundError:
        return print_.no_renamings()

    try:
        editable_file_path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
    except Exception as e:
        print_.fail(str(e))
        return print_.no_renamings()

    try:
        editable_file_path.write_text(get_editable_text(inodes_paths))
    except FileNotFoundError:
        return print_.no_renamings("The editable file was deleted.")

    try:
        editor_command = get_editor_command(editable_file_path)
    except UnsupportedOSError:
        return print_.no_renamings()

    try:
        subprocess.run(editor_command, check=True)
    except subprocess.CalledProcessError:
        return print_.no_renamings()

    try:
        edited_text = EditedText(editable_file_path.read_text())
    except FileNotFoundError:
        return print_.no_renamings("The editable file was deleted.")

    try:
        clauses = parse_edited_text(edited_text, inodes_paths)
    except (UnknownInodeError, TabulationError, ValidationError):
        return print_.no_renamings()

    try:
        arcs = secure_clauses(FileSystem(), clauses)
    except (SeveralTargetsError, SeveralSourcesError, DuplicatedClauseError):
        return print_.no_renamings()

    renamer = Renamer()
    try:
        renamer.perform_renamings(arcs)
    except RecoverableRenamingError:
        try:
            renamer.rollback_renamings()
            return print_.no_renamings()
        except: # Unknow error during rollback.
            return print_.fail("Rollback failed.")


def cli_arguments():
    """
    CLI argument parser.

    Returns:
        `parser.parse_args()` dict containing the parsed arguments.
    """
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        usage=f"\n{Path(__file__).name} [-p paths] [-f file] [-h help]",
        description=f"\nFILE RENAMER",
    )

    parser.add_argument(
        "-p",
        "--paths",
        nargs="+",
        help=f"The paths to rename.",
        action="store",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=f"Parse paths stored in a file (newline separated).",
        action="store",
    )

    parser.add_argument(
        "-u",
        "--undo",
        help=f"Undo completed renamings from the previous session.",
        action="store_true",
    )

    return parser.parse_args()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
