from pathlib import Path
import logging
import re
from typing import List

from src.goodies import print_exit, print_success
from src.user_types import Renaming


def set_logger(log_path: Path):
    logging.basicConfig(filename=log_path, filemode="w", level=logging.DEBUG)


def perform_renamings(renamings: List[Renaming]):
    try:
        for (i, renaming) in enumerate(renamings):
            rename_and_log(renaming)
        print_success("Success.")
    except OSError:
        logging.warning("Failed renaming.")
        rollback_renamings(renamings[:i])


def rollback_renamings(renamings: List[Renaming]):
    try:
        for renaming in reversed(renamings):
            rename_and_log(swap(renaming))
        logging.warning("Rolled back.")
        print_exit("Recoverable error during the renaming. No changes.")
    except OSError:
        logging.critical("Failed rollback.")
        log_path = logging.getLoggerClass().root.handlers[0].baseFilename
        print_exit(f"Unrecoverable error during the renaming, see '{log_path}'.")


def rename_and_log(renaming: Renaming):
    renaming.source.rename(renaming.target)
    logging.info(f"SOURCE:{renaming.source}")
    logging.info(f"TARGET:{renaming.target}")


def swap(renaming: Renaming) -> Renaming:
    """Return a copy of the given renaming where the source and the target are swapped."""
    return Renaming(Path(renaming.target), Path(renaming.source))


def undo_renamings(
    log_path: Path,
    find_all_renamings=re.compile(r"(?m)^INFO:\w+:SOURCE:(.+)\nINFO:\w+:TARGET:(.+)").findall,
):
    """Read a log file and apply the renamings in reversed and by swapping sources and targets."""
    perform_renamings(list(map(swap, reversed(find_all_renamings(log_path.read_text())))))
