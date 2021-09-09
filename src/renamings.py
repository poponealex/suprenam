from typing import List
from src.user_types import Clause

from src.goodies import print_success, print_exit

import logging


def perform_renamings(clauses: List[Clause], log_file_path):
    sources_and_targets = [(path, path.parent / new_name) for (path, new_name) in clauses]
    logging.basicConfig(filename=log_file_path, filemode="w", level=logging.DEBUG)
    try:
        for (i, (source, target)) in enumerate(sources_and_targets):
            source.rename(target)
            logging.info(f"{source} > {target}")
        print_success("Success.")
    except OSError:
        rollback_renamings(reversed(sources_and_targets[:i]), log_file_path)


def rollback_renamings(targets_and_sources, log_file_path):
    try:
        for (target, source) in targets_and_sources:
            source.rename(target)
            logging.info(f"{source} > {target}")
        logging.warning("Rolled back.")
        print_exit("Recoverable error during the renaming. No changes.")
    except OSError:
        logging.critical("Failed.")
        print_exit(f"Unrecoverable error during the renaming, see '{log_file_path}'.")
