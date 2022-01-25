import logging
import re
from pathlib import Path
from typing import List

from src.printer import print_
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


def show_log_file():  # pragma: no cover
    """Print the contents of the log file (for testing purposes only)."""
    try:
        log_path = get_log_path()
        print_(f"Log file at '{log_path}':")
        print_(log_path.read_text())
    except FileNotFoundError as e:
        print_.warning(f"Log file not found: {e}.")


def perform_renamings(arcs: List[Arc]):
    """
    Perform the renamings specified by the list of arcs (source path, target path), and
    log them one by one.

    Args:
        arcs: list of couples (source_path, target_path)
    """
    create_new_log_file()

    # Perform the actual renaming operations.
    n = len(arcs)
    print_(f"Renaming {n} items...")
    try:
        for (i, arc) in enumerate(arcs):
            rename_and_log_one_file(arc)
        print_arcs(arcs)
        print_.newline()
        return print_.success(f"Successfully renamed all {n} item{'s'[:n^1]}.")
    except Exception as e:
        logging.warning(str(e))
        print_.fail(str(e))

    # Rollback the first renaming operations.
    print_(f"Rolling back the first {i} renaming{'s'[:i^1]}...")
    for (source, target) in reversed(arcs[:i]):
        rename_and_log_one_file(Arc(target, source))
    logging.warning("Rolled back.")
    print_.success("Rolled back.")
    raise RecoverableRenamingError


def rename_and_log_one_file(arc: Arc):
    arc.source.rename(arc.target)
    logging.info(f"SOURCE:{arc.source}")
    logging.info(f"TARGET:{arc.target}")


def undo_renamings(get_arcs=re.compile(r"(?m)^\w+:\w+:SOURCE:(.+)\n\w+:\w+:TARGET:(.+)").findall):
    """Read a log file and apply the reversed renamings."""
    log_path = get_log_path()
    arcs = [Arc(Path(target), Path(source)) for (source, target) in get_arcs(log_path.read_text())]
    n = len(arcs)
    print_(f"Undoing the {n} renamings found in the log file...")
    create_new_log_file()
    for arc in reversed(arcs):
        rename_and_log_one_file(arc)
    print_arcs(arcs)
    print_.newline()
    print_.success(f"Successfully unrenamed all {n} item{'s'[:n^1]}.")


def print_arcs(arcs: List[Arc]):
    previous_parent = Path()
    for (source, target) in arcs:
        if source.parent != previous_parent:
            print_.newline()
            print_(f"{source.parent}")
            previous_parent = source.parent
        print_(f"{source.name} -> {target.name}")
