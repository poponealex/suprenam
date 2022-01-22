import logging
import re
from pathlib import Path
from typing import List

from src.goodies import *
from src.user_types import Arc

LOG_DIR = Path.home() / ".suprenam"
LOG_NAME = "previous_session.log"


def perform_renamings(
    arcs: List[Arc],
    log_path: Path = LOG_DIR / LOG_NAME,
):
    """
    Perform the renamings specified by the list of arcs (source path, target path), and
    log them one by one.

    Args:
        arcs: list of couples (source_path, target_path)
        log_path: path to the log file
    """
    # Ensure the log directory exists.
    log_path.parent.mkdir(
        parents=True,  # any missing parents of this path are created as needed
        exist_ok=True,  # if the directory already exists, do not raise an exception
    )

    # Remove all handlers associated with the root logger object and create a NEW log file.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=log_path, filemode="w", level=logging.DEBUG)

    # Perform the renaming operations.
    try:
        for (i, arc) in enumerate(arcs):
            rename_and_log_one_file(arc)
        print_success("Success.")
    except OSError:
        logging.warning("Failed renaming.")
        rollback_renamings(arcs[:i])


def rollback_renamings(arcs: List[Arc]):
    try:
        for (source, target) in reversed(arcs):
            rename_and_log_one_file(Arc(target, source))
        logging.warning("Rolled back.")
        print_exit("Recoverable error during the renaming. No changes.")
    except OSError:
        logging.critical("Failed rollback.")
        log_path = logging.getLoggerClass().root.handlers[0].baseFilename  # type: ignore
        print_exit(f"Unrecoverable error during the renaming, see '{log_path}'.")


def undo_renamings(
    log_path: Path = LOG_DIR / LOG_NAME,
    find_all_arcs=re.compile(r"(?m)^INFO:\w+:SOURCE:(.+)\nINFO:\w+:TARGET:(.+)").findall,
):
    """Read a log file and apply the renamings in reverse and by swapping sources and targets."""
    arcs = []
    for (source, target) in reversed(find_all_arcs(log_path.read_text())):
        arcs.append(Arc(Path(target), Path(source)))
    perform_renamings(arcs)


def rename_and_log_one_file(arc: Arc):
    arc.source.rename(arc.target)
    logging.info(f"SOURCE:{arc.source}")
    logging.info(f"TARGET:{arc.target}")


def show_log_file(log_path: Path = LOG_DIR / LOG_NAME):
    """Print the contents of the log file (for testing purposes only)."""
    print(f"Log file at '{log_path}':")
    try:
        print(log_path.read_text())
    except FileNotFoundError:
        print(f"{WARNING}Not found.{RESET}")
