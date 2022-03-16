import subprocess
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Dict, Any

sys.path[0:0] = ["."]

from src.file_system import FileSystem
from src.get_editable_text import get_editable_text
from src.get_editor_command import get_editor_command
from src.context import Context
from src.parse_edited_text import parse_edited_text
from src.paths_to_inodes_paths import paths_to_inodes_paths
from src.renamings import Renamer
from src.secure_clauses import secure_clauses
from src.user_errors import *
from src.user_types import EditedText


def main():
    context = Context()
    context.logger.create_new_log_file()
    context.logger.info("Starting the program.")
    context.logger.info("Parsing arguments.")
    kwargs = cli_arguments()
    context.logger.info("Parsing arguments done.")
    if kwargs["paths"]:
        do_renamings(context, **kwargs)
    else:
        undo_renamings(context)
    context.logger.info("Exiting the program.")


def undo_renamings(context: Context):
    logger = context.logger
    print_ = context.print_
    logger.info("Undoing renamings.")
    renamer = Renamer(context)
    try:
        arcs_for_undoing = renamer.get_arcs_for_undoing(logger.previous_log_contents)
        opening = "The previous renaming session was undone."
        closing = "Launch Suprenam again to restore."
        n = renamer.perform_renamings(arcs_for_undoing)
        if n == 0:
            print_.abort(f"{opening} There was no renaming to undo.")
        elif n == 1:
            print_.success(f"{opening} The sole renaming was undone. {closing}")
        else:
            print_.success(f"{opening} All {n} renamings were undone. {closing}")
    except RecoverableRenamingError:
        try:
            renamer.rollback_renamings()
            print_.abort("The renamings failed, but were successfully rolled back.")
        except Exception as e:
            return print_.fail(f"Unrecoverable failure during rollback: {e}")
    except Exception as e:  # Unknown problem with the log file, e.g. not found
        return print_.fail(f"Unrecoverable failure during undo: {e}")
    logger.info("Undoing renamings done.")


def do_renamings(context: Context, **kwargs):
    logger = context.logger
    print_ = context.print_
    logger.info("Constructing the list of items to rename.")

    paths: List[Path] = []
    if len(kwargs["paths"]) > 1:
        logger.info("The paths of several items to rename are provided.")
        paths.extend(map(Path, kwargs["paths"]))
    else:  # `do_renamings` cannot be called without at least one path. So there is exactly one.
        single_path = Path(kwargs["paths"][0])
        logger.info(f"A single path is provided: {single_path}.")
        if single_path.is_dir():
            logger.info(f"It is a directory: it and its children are to be renamed.")
            paths.append(single_path)
            paths.extend(single_path.iterdir())
        elif single_path.is_file() and single_path.suffix == ".txt":
            logger.info(f"It is a text file containing the paths of the items to rename.")
            paths.extend(map(Path, filter(None, single_path.read_text().splitlines())))
        else:
            logger.info(f"It is either a missing or a non-text file: default to rename it.")
            paths.append(single_path)
            # The case of a missing single file will be catched by `paths_to_inodes_paths()`.

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
        editor_command = get_editor_command(context, editable_file_path)
        logger.info(f"The command is {editor_command}.")
    except Exception as e:
        return print_.abort(str(e))

    logger.info("Opening the editable text file in the editor and waiting it to be closed.")
    try:
        subprocess.run(editor_command, shell=True, check=True)
        logger.info("Command executed without process error.")
    except subprocess.CalledProcessError:
        return print_.abort(f"The command '{editor_command}' failed.")

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

    logger.info("Converting the clauses into a “safe” sequence of renamings.")
    try:
        arcs = secure_clauses(FileSystem(), clauses)
        logger.info(f"Converted clauses into {len(arcs)} arcs.")
    except Exception as e:
        return print_.abort(str(e))

    logger.info("Performing the actual renamings.")
    renamer = Renamer(context)
    try:
        n = renamer.perform_renamings(arcs)
        if n == 0:
            print_.abort(f"Nothing was changed in the name list.")
        elif n == 1:
            print_.success(f"One item was renamed.")
        else:
            print_.success(f"All {n} items were renamed.")
    except RecoverableRenamingError:
        logger.warning("Renaming performed with a recoverable error.")
        try:
            opening = "The renamings failed, but don't worry:"
            n = renamer.rollback_renamings()
            if n == 0:
                print_.abort(f"{opening} there was nothing to roll back.")
            elif n == 1:
                print_.abort(f"{opening} the only renaming was rolled back.")
            else:
                print_.abort(f"{opening} all {n} renamings were rolled back.")
        except Exception as e:
            return print_.fail(
                f"Unrecoverable failure during rollback: {e}"
                "Some files may have been renamed, some not."
                f"Please check the log file at '{logger.path}'."
            )


def cli_arguments() -> Dict[str, Any]:
    """
    CLI argument parser.

    Returns:
        A dictionary containing the parsed arguments.
    """
    parser = ArgumentParser(description="Easily rename items via your favorite text editor.")
    parser.add_argument(
        "paths",
        type=str,
        nargs="*",
        help=(
            "either several items to rename, "
            "or a text file enumerating the items to rename, "
            "or a directory whose children are to be renamed"
        ),
    )
    return vars(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
