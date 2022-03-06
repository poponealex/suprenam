import re
import subprocess
from pathlib import Path
from typing import List

from src.logger import logger
from src.printer import print_
from src.user_errors import RecoverableRenamingError
from src.user_types import Arc


class Renamer:
    def __init__(self, testing: bool = False):
        if testing:
            logger.create_new_log_file()

    def perform_renamings(self, arcs: List[Arc]):
        """
        Perform the renamings specified by the list of arcs (source path, target path), and
        log them one by one.

        Args:
            arcs: list of couples (source_path, target_path)
        """
        n = len(arcs)
        print_(f"Renaming {n} items...")
        logger.info(f"{n} item{'s'[:n^1]} to rename.")
        try:
            self.rename_and_log_all_files(arcs)
            logger.info(f"{n} item{'s'[:n^1]} renamed.")
            print_(f"{n} item{'s'[:n^1]} renamed.")
            if n == 0:
                return f"Nothing to rename."
            elif n == 1:
                return f"1 item was renamed."
            else:
                return f"All {n} items were renamed."
        except Exception as e:
            logger.warning(f"perform_renamings: {e}")
            raise RecoverableRenamingError(f"{e}.")

    def rollback_renamings(self):
        """
        Rollback the first renaming operations.

        The inverse renaming are appended to the log file.
        """
        n = len(self.arcs_to_rollback)
        print_(f"Rolling back the first {n} renaming{'s'[:n^1]}...")
        logger.info(f"{n} renaming{'s'[:n^1]} to roll back.")
        try:
            self.rename_and_log_all_files(self.arcs_to_rollback)
            logger.info(f"{n} renaming{'s'[:n^1]} rolled back.")
            if n == 0:
                return f"there was nothing to roll back."
            elif n == 1:
                return f"the only renaming was rolled back."
            else:
                return f"all {n} renamings were rolled back."
        except Exception as e:
            logger.error(f"rollback_renamings: {e}")
            raise

    def get_arcs_for_undoing(
        self,
        previous_log_text: str,
        get_logged_arcs=re.compile(r"(?m)^\w+:\w+:SOURCE:(.+)\tTARGET:(.+)").findall,
    ):
        """Read a log file and calculate the reversed renamings."""
        if re.search(r"(?m)^ERROR:", previous_log_text):  # The log file contains an error.
            raise ValueError("The previous rollback failed. Undoing is not possible.")
        arcs = []
        for (source, target) in reversed(get_logged_arcs(previous_log_text)):
            arcs.append(Arc(Path(target), Path(source)))
        return arcs

    def rename_and_log_all_files(self, arcs: List[Arc]):
        self.arcs_to_rollback: List[Arc] = []
        for (source, target) in arcs:
            try:
                subprocess.run(
                    [
                        "git", # git fails when launched from a non-versioned directory.
                        "-C", # This option runs git as if it was started...
                        source.parent, #  ... in the source's parent directory.
                        "mv",
                        source.name,
                        target.name,
                    ],
                    check=True,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                source.rename(target)
            self.arcs_to_rollback.insert(0, Arc(target, source))
            logger.info(f"SOURCE:{source}\tTARGET:{target}")
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
