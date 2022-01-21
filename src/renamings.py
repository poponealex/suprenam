import logging
import re
from pathlib import Path
from typing import List

from src.goodies import *
from src.user_types import Renaming

LOG_DIR = Path.home() / ".suprenam"
LOG_NAME = "previous_session.log"


def perform_renamings(
    renamings: List[Renaming],
    log_path: Path = LOG_DIR / LOG_NAME,
):
    """
    Given a list of renaming operations, perform them and log them in a log file.

    Args:
        renamings: list of Renaming objects
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
        for (i, renaming) in enumerate(renamings):
            rename_and_log_one_file(renaming)
        print_success("Success.")
    except OSError:
        logging.warning("Failed renaming.")
        rollback_renamings(renamings[:i])


def rollback_renamings(renamings: List[Renaming]):
    try:
        for renaming in reversed(renamings):
            rename_and_log_one_file(swap_source_and_target(renaming))
        logging.warning("Rolled back.")
        print_exit("Recoverable error during the renaming. No changes.")
    except OSError:
        logging.critical("Failed rollback.")
        log_path = logging.getLoggerClass().root.handlers[0].baseFilename  # type: ignore
        print_exit(f"Unrecoverable error during the renaming, see '{log_path}'.")


def undo_renamings(
    log_path: Path = LOG_DIR / LOG_NAME,
    find_all_renamings=re.compile(r"(?m)^INFO:\w+:SOURCE:(.+)\nINFO:\w+:TARGET:(.+)").findall,
):
    """Read a log file and apply the renamings in reverse and by swapping sources and targets."""
    renamings = []
    for source, target in reversed(find_all_renamings(log_path.read_text())):
        renamings.append(swap_source_and_target(Renaming(Path(source), Path(target))))
    perform_renamings(renamings)


def rename_and_log_one_file(renaming: Renaming):
    renaming.source.rename(renaming.target)
    logging.info(f"SOURCE:{renaming.source}")
    logging.info(f"TARGET:{renaming.target}")


def swap_source_and_target(renaming: Renaming) -> Renaming:
    """Return a copy of the given renaming where the source and the target are swapped."""
    return Renaming(Path(renaming.target), Path(renaming.source))


def show_log_file(log_path: Path = LOG_DIR / LOG_NAME):
    """Print the contents of the log file (for testing purposes only)."""
    print(f"Log file at '{log_path}':")
    try:
        print(log_path.read_text())
    except FileNotFoundError:
        print(f"{WARNING}Not found.{RESET}")
