import logging
import re
from pathlib import Path
from typing import List

from src.printer import print_
from src.user_errors import RecoverableRenamingError
from src.user_types import Arc


class Renamer:

    LOG_DIR = Path.home() / ".suprenam"
    LOG_NAME = "previous_session.log"
    get_logged_arcs = re.compile(r"(?m)^\w+:\w+:SOURCE:(.+)\n\w+:\w+:TARGET:(.+)").findall

    def __init__(self, log_path: Path = LOG_DIR / LOG_NAME):
        """Create a log file at the specified path."""
        # Ensure the log directory exists.
        log_path.parent.mkdir(
            parents=True,  # any missing parents of this path are created as needed
            exist_ok=True,  # if the directory already exists, do not raise an exception
        )
        self.log_path = log_path

    def create_new_log_file(self):
        """Remove all handlers associated with the root logger object and create a NEW log file."""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.log_path, filemode="w", level=logging.DEBUG)

    def perform_renamings(self, arcs: List[Arc]):
        """
        Perform the renamings specified by the list of arcs (source path, target path), and
        log them one by one.

        Args:
            arcs: list of couples (source_path, target_path)
        """
        self.create_new_log_file()
        n = len(arcs)
        print_(f"Renaming {n} items...")
        try:
            self.rename_and_log_all_files(arcs)
            if n == 0:
                return print_.success(f"Nothing to rename.")
            elif n == 1:
                return print_.success(f"1 item was renamed.")
            else:
                return print_.success(f"All {n} items were renamed.")
        except Exception as e:
            logging.warning(str(e))
            print_.fail(str(e))
            raise RecoverableRenamingError

    def rollback_renamings(self):
        """
        Rollback the first renaming operations.

        The inverse renaming are appended to the log file.
        """
        n = len(self.arcs_to_rollback)
        print_(f"Rolling back the first {n} renaming{'s'[:n^1]}...")
        logging.info("rollback")
        try:
            self.rename_and_log_all_files(self.arcs_to_rollback)
            self.log_path.write_text("")  # no need to keep a symmetric sequence of renamings!
            if n == 0:
                return print_.success(f"Nothing to rollback.")
            elif n == 1:
                return print_.success(f"1 renaming was rolled back.")
            else:
                return print_.success(f"All {n} renamings were rolled back.")
        except Exception as e:
            logging.error(f"rollback:{e}")
            print_.fail(str(e))
            raise

    def undo_renamings(self):
        """Read a log file and apply the reversed renamings."""
        try:
            log_text = self.log_path.read_text()
        except Exception as e:
            print_.fail(str(e))
            raise
        if re.search(r"(?m)^ERROR:", log_text):
            print_.fail("The previous rollback failed. Undoing is not possible.")
            raise ValueError
        arcs = []
        for (source, target) in reversed(self.get_logged_arcs(log_text)):
            arcs.append(Arc(Path(target), Path(source)))
        self.perform_renamings(arcs)

    def rename_and_log_all_files(self, arcs: List[Arc]):
        self.arcs_to_rollback: List[Arc] = []
        for (source, target) in arcs:
            source.rename(target)
            self.arcs_to_rollback.insert(0, Arc(target, source))
            logging.info(f"SOURCE:{source}")
            logging.info(f"TARGET:{target}")
        self.print_arcs(arcs)
        print_.newline()

    def print_arcs(self, arcs: List[Arc]):
        previous_parent = Path()
        for (source, target) in arcs:
            if source.parent != previous_parent:
                print_.newline()
                print_(f"{source.parent}")
                previous_parent = source.parent
            print_(f"{source.name} -> {target.name}")

    def get_log_contents(self):  # pragma: no cover
        """get the contents of the log file (for testing purposes only)."""
        return self.log_path.read_text().strip()
