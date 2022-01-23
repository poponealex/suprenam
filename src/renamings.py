import logging
import re
from pathlib import Path
from typing import List

from src.goodies import *
from src.user_errors import RecoverableRenamingError
from src.user_types import Arc

LOG_DIR = Path.home() / ".suprenam"
LOG_NAME = "previous_session.log"


def create_new_log_file(log_path: Path = LOG_DIR / LOG_NAME):
    """Create a log file at the specified path."""
    # Ensure the log directory exists.
    log_path.parent.mkdir(
        parents=True,  # any missing parents of this path are created as needed
        exist_ok=True,  # if the directory already exists, do not raise an exception
    )
    # Remove all handlers associated with the root logger object and create a NEW log file.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=log_path, filemode="w", level=logging.DEBUG)
    return log_path


def get_log_path() -> Path:
    """Return the path to the log file."""
    return Path(logging.getLoggerClass().root.handlers[0].baseFilename)  # type: ignore


def show_log_file():
    """Print the contents of the log file (for testing purposes only)."""
    try:
        log_path = get_log_path()
        print(f"Log file at '{log_path}':")
        print(log_path.read_text())
    except FileNotFoundError as e:
        print_warning(f"Log file not found: {e}.")


def perform_renamings(arcs: List[Arc]):
    """
    Perform the renamings specified by the list of arcs (source path, target path), and
    log them one by one.

    Args:
        arcs: list of couples (source_path, target_path)
    """
    create_new_log_file()

    # Perform the actual renaming operations.
    try:
        for (i, arc) in enumerate(arcs):
            rename_and_log_one_file(arc)
        n = len(arcs)
        return print_success(f"Successfully renamed all {n} file{'s'[:n^1]}.")
    except Exception as e:
        logging.warning(str(e))
        print_fail(str(e))

    # Rollback the first renaming operations.
    print(f"Rolling back the first {i} renaming{'s'[:i^1]}...")
    perform_inverse_renamings(arcs[:i])
    logging.warning("Rolled back.")
    print_success("Rolled back.")
    raise RecoverableRenamingError


def perform_inverse_renamings(arcs: List[Arc]):
    for (source, target) in reversed(arcs):
        rename_and_log_one_file(Arc(Path(target), Path(source)))


def rename_and_log_one_file(arc: Arc):
    arc.source.rename(arc.target)
    logging.info(f"SOURCE:{arc.source}")
    logging.info(f"TARGET:{arc.target}")


def undo_renamings(
    find_logged_arcs=re.compile(r"(?m)^INFO:\w+:SOURCE:(.+)\nINFO:\w+:TARGET:(.+)").findall,
):
    """Read a log file and apply the reversed renamings."""
    print("Undoing the renamings found in the log file...")
    log_path = get_log_path()
    arcs = list(find_logged_arcs(log_path.read_text()))
    create_new_log_file()
    perform_inverse_renamings(arcs)
    n = len(arcs)
    print_success(f"Successfully unrenamed all {n} file{'s'[:n^1]}.")
