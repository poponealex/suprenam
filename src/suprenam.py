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
from src.goodies import *
from src.parse_edited_text import parse_edited_text
from src.paths_to_inodes_paths import paths_to_inodes_paths
from src.renamings import perform_renamings, undo_renamings
from src.secure_clauses import secure_clauses
from src.user_errors import *
from src.user_types import EditedText


def main():
    args = cli_arguments()

    if args.undo:
        try:
            return undo_renamings()
        except Exception as e:
            return print_fail(f"Undoing failed: {str(e)}.")

    # Construct the list of files to rename.
    paths = []
    if args.paths:  # a list of files to rename was provided
        paths.extend(map(Path, args.paths))
    if args.file:  # a file containing the paths to rename was provided
        paths.extend(Path(path) for path in Path(args.file).read_text().split("\n") if path)
    if not paths:
        print_fail("Please provide at least one file to rename.")
        return abort_without_renaming()

    run_on_path_list(paths)


def run_on_path_list(paths: List[Path]):

    # Create a mapping from inodes to paths.
    try:
        inodes_paths = paths_to_inodes_paths(paths)
    except FileNotFoundError:
        return abort_without_renaming()

    try:
        editable_file_path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
    except Exception as e:
        print_fail(str(e))
        return abort_without_renaming()

    try:
        editable_file_path.write_text(get_editable_text(inodes_paths))
    except FileNotFoundError:
        return abort_without_renaming("The editable file was deleted.")

    try:
        editor_command = get_editor_command(editable_file_path)
    except UnsupportedOSError:
        return abort_without_renaming()

    try:
        subprocess.run(editor_command, check=True)
    except subprocess.CalledProcessError:
        return abort_without_renaming()

    try:
        edited_text = EditedText(editable_file_path.read_text())
    except FileNotFoundError:
        return abort_without_renaming("The editable file was deleted.")

    try:
        clauses = parse_edited_text(edited_text, inodes_paths)
    except (UnknownInodeError, TabulationError, ValidationError):
        return abort_without_renaming()

    try:
        arcs = secure_clauses(FileSystem(), clauses)
    except (SeveralTargetsError, SeveralSourcesError, DuplicatedClauseError):
        return abort_without_renaming()

    try:
        perform_renamings(arcs)
    except RecoverableRenamingError:
        return abort_without_renaming()
    except Exception as e:
        print_fail(f"Rollback failed: {str(e)}.")


def cli_arguments():
    """
    CLI argument parser.

    Returns:
        `parser.parse_args()` dict containing the parsed arguments.
    """
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        usage=f"\n{WARNING}{Path(__file__).name} [-p paths] [-f file] [-h help]{RESET}",
        description=f"{OK}\nFILE RENAMER{RESET}",
    )

    parser.add_argument(
        "-p",
        "--paths",
        nargs="+",
        help=f"{OK}The paths to rename.{RESET}",
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
        action="store_true",
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
