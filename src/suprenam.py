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
from src.parse_edited_text import parse_edited_text
from src.paths_to_inodes_paths import paths_to_inodes_paths
from src.printer import print_
from src.renamings import Renamer
from src.secure_clauses import secure_clauses
from src.user_errors import *
from src.user_types import EditedText


def main_wrapper():
    previous_log_text = logger.get_contents()
    logger.create_new_log_file()
    logger.info("Starting the program.")
    main(previous_log_text)
    logger.info("Exiting the program.")


def main(previous_log_text: str):
    logger.info("Parsing arguments.")
    args = cli_arguments()
    logger.info("Parsing arguments done.")

    if not args.undo:
        logger.info("Constructing the list of items to rename.")
        paths: List[Path] = []
        if args.paths:
            logger.info("A list of items to rename was provided.")
            paths.extend(map(Path, args.paths))
        if args.file:
            logger.info("A file containing the paths to rename was provided.")
            paths.extend(Path(path) for path in Path(args.file).read_text().split("\n") if path)
        if not paths:
            logger.info("No paths to rename were provided.")
            return print_.abort("Please provide at least one file to rename.")
        logger.info("Running on path list.")
        run_on_path_list(paths)
        logger.info("Running on path list done.")
    else:
        logger.info("Undoing renamings.")
        renamer = Renamer()
        try:
            arcs_for_undoing = renamer.get_arcs_for_undoing(previous_log_text)
            logger.info(str(arcs_for_undoing))
            message = renamer.perform_renamings(arcs_for_undoing)
            print_.success(
                f"The previous renaming session was undone. {message} "
                "Launch Suprenam again to restore."
            )
        except RecoverableRenamingError:
            try:
                renamer.rollback_renamings()
                print_.abort("The renamings failed, but were successfully rolled back.")
            except Exception as e:
                return print_.fail(f"Unrecoverable failure during rollback: {e}")
        except Exception as e:  # Unknown problem with the log file, e.g. not found
            return print_.fail(f"Unrecoverable failure during undo: {e}")
        logger.info("Undoing renamings done.")


def run_on_path_list(paths: List[Path]):

    logger.info("Creating a mapping from inodes to paths.")
    try:
        inodes_paths = paths_to_inodes_paths(paths)
        logger.info("Creating a mapping from inodes to paths done.")
    except Exception as e:
        return print_.abort(str(e))

    logger.info("Creating a temporary text file for the list to be edited.")
    try:
        editable_file_path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".tsv").name)
        logger.info(f"Editable file path: {repr(editable_file_path)}.")
    except Exception as e:
        return print_.abort(f"Failed to create a temporary file: {e}")

    logger.info("Populating the temporary text file with the list to be edited.")
    try:
        editable_file_path.write_text(get_editable_text(inodes_paths))
        logger.info(f"Editable file content: populated.")
    except Exception as e:
        return print_.abort(f"Failed to populate the temporary file: {e}")

    logger.info("Retrieving a command to edit the temporary text file.")
    try:
        editor_command = get_editor_command(editable_file_path)
        logger.info(f"The command is {' '.join(editor_command)}.")
    except UnsupportedOSError:
        return

    logger.info("Opening the editable text file in the editor and waiting it to be closed.")
    try:
        subprocess.run(editor_command, check=True)
        logger.info("Command executed without process error.")
    except subprocess.CalledProcessError:
        return print_.abort(f"The command {' '.join(editor_command)} failed.")

    logger.info("Retrieving the content of the edited text file.")
    try:
        edited_text = EditedText(editable_file_path.read_text())
        logger.info("Line count in the edited text file: %s." % edited_text.count("\n"))
    except Exception as e:
        return print_.abort(f"Failed to read the edited text file: {e}")

    logger.info("Parsing the edited text into renaming clauses.")
    try:
        clauses = parse_edited_text(edited_text, inodes_paths)
        logger.info(f"Parsed edited text into {len(clauses)} clauses.")
    except Exception as e:
        return print_.abort(str(e))

    logger.info("Converting the clauses into a 'safe' sequence of renamings.")
    try:
        arcs = secure_clauses(FileSystem(), clauses)
        logger.info(f"Converted clauses into {len(arcs)} arcs.")
    except Exception as e:
        return print_.abort(str(e))

    logger.info("Performing the actual renamings.")
    renamer = Renamer()
    try:
        message = renamer.perform_renamings(arcs)
        return print_.success(message)
    except RecoverableRenamingError:
        logger.warning("Renaming performed with a recoverable error.")
        try:
            message = renamer.rollback_renamings()
            return print_.abort(f"The renamings failed, but don't worry: {message}.")
        except Exception as e:
            return print_.fail(
                f"Unrecoverable failure during rollback: {e}"
                "Some files may have been renamed, some not."
                "Please check the log file at `~/.suprenam/log.txt`."
            )


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
    main_wrapper()
