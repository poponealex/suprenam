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
from src.logger import logger
from src.printer import print_
from src.parse_edited_text import parse_edited_text
from src.paths_to_inodes_paths import paths_to_inodes_paths
from src.renamings import Renamer
from src.secure_clauses import secure_clauses
from src.user_errors import *
from src.user_types import EditedText


def main():
    logger.info("Parsing arguments.")
    args = cli_arguments()
    logger.info("Parsing arguments done.")

    if args.undo:
        logger.info("Undoing renamings.")
        renamer = Renamer()
        try:
            arcs_for_undoing = renamer.get_arcs_for_undoing()
            renamer.perform_renamings(arcs_for_undoing)
        except RecoverableRenamingError:
            try:
                renamer.rollback_renamings()
                print_.no_renamings()
            except: # Unknow error during rollback.
                print_.fail("Rollback failed.")
        except: # Unknown problem with the log file, e.g. not found
            print_.fail("Undo failed.")
        logger.info("Undoing renamings done.")
        return print_.flush_buffer_and_exit()

    logger.info("Constructing the list of items to rename.")
    paths = []
    if args.paths:
        logger.info("A list of items to rename was provided.")
        paths.extend(map(Path, args.paths))
    if args.file:
        logger.info("A file containing the paths to rename was provided.")
        paths.extend(Path(path) for path in Path(args.file).read_text().split("\n") if path)
    if not paths:
        logger.info("No paths to rename were provided.")
        return print_.no_renamings("Please provide at least one file to rename.")

    logger.info("Running on path list.")
    run_on_path_list(paths)
    logger.info("Running on path list done.")
    return print_.flush_buffer_and_exit()


def run_on_path_list(paths: List[Path]):

    logger.info("Creating a mapping from inodes to paths.")
    try:
        inodes_paths = paths_to_inodes_paths(paths)
    except FileNotFoundError:
        return print_.no_renamings()

    logger.info("Creating a temporary text file for the list to be edited.")
    try:
        editable_file_path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
        logger.info(f"Editable file path: {repr(editable_file_path)}.")
    except Exception as e:
        print_.fail(str(e))
        return print_.no_renamings()

    logger.info("Populating the temporary text file with the list to be edited.")
    try:
        editable_file_path.write_text(get_editable_text(inodes_paths))
        logger.info(f"Editable file content: populated.")
    except FileNotFoundError:
        return print_.no_renamings("The editable file was deleted.")

    logger.info("Retrieving a command to edit the temporary text file.")
    try:
        editor_command = get_editor_command(editable_file_path)
        logger.info(f"The command is {' '.join(editor_command)}.")
    except UnsupportedOSError:
        return print_.no_renamings()

    logger.info("Opening the editable text file in the editor and waiting it is closed.")
    try:
        subprocess.run(editor_command, check=True)
        logger.info("Command executed without process error.")
    except subprocess.CalledProcessError:
        return print_.no_renamings()

    logger.info("Retrieving the content of the edited text file.")
    try:
        edited_text = EditedText(editable_file_path.read_text())
        logger.info("Line count in the edited text file:,", edited_text.count('\n'))
    except FileNotFoundError:
        return print_.no_renamings("The editable file was deleted.")

    logger.info("Parsing the edited text into renaming clauses.")
    try:
        clauses = parse_edited_text(edited_text, inodes_paths)
        logger.info(f"Parsed edited text into {len(clauses)} clauses.")
    except (UnknownInodeError, TabulationError, ValidationError):
        return print_.no_renamings()

    logger.info("Converting the clauses into a 'safe' sequence of renamings.")
    try:
        arcs = secure_clauses(FileSystem(), clauses)
        logger.info(f"Converted clauses into {len(arcs)} arcs.")
    except (SeveralTargetsError, SeveralSourcesError, DuplicatedClauseError):
        return print_.no_renamings()

    logger.info("Performing the actual renamings.")
    renamer = Renamer()
    try:
        renamer.perform_renamings(arcs)
        logger.info("Renaming performed without errors.")
    except RecoverableRenamingError:
        logger.info("Renaming performed with recoverable errors.")
        try:
            renamer.rollback_renamings()
            return print_.no_renamings()
        except:
            logger.info("Unknown error during rollback.")
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
    logger.create_new_log_file()
    logger.info("Starting the program.")
    main()
    logger.info("Exiting the program.")
