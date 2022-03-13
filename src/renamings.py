import re
import subprocess
from pathlib import Path
from typing import List

from src.context import Context
from src.user_errors import RecoverableRenamingError
from src.user_types import Arc


class Renamer:
    def __init__(self, context: Context, testing: bool = False):
        self.logger = context.logger
        self.print_ = context.print_
        if testing:
            self.logger.create_new_log_file()

    def perform_renamings(self, arcs: List[Arc]) -> int:
        """
        Perform the renamings specified by the list of arcs (source path, target path), and
        log them one by one.

        Args:
            arcs: list of couples (source_path, target_path)
        """
        n = len(arcs)
        self.print_(f"Renaming {n} items...")
        self.logger.info(f"{n} item{'s'[:n^1]} to rename.")
        try:
            self.rename_and_log_all_files(arcs)
            self.logger.info(f"{n} item{'s'[:n^1]} renamed.")
            self.print_(f"{n} item{'s'[:n^1]} renamed.")
            return n
        except Exception as e:
            self.logger.warning(f"perform_renamings: {e}")
            raise RecoverableRenamingError(f"{e}.")

    def rollback_renamings(self) -> int:
        """
        Rollback the first renaming operations.

        Note: the inverse renamings are appended to the log file.
        """
        n = len(self.arcs_to_rollback)
        self.print_(f"Rolling back the first {n} renaming{'s'[:n^1]}...")
        self.logger.info(f"{n} renaming{'s'[:n^1]} to roll back.")
        try:
            self.rename_and_log_all_files(self.arcs_to_rollback)
            self.logger.info(f"{n} renaming{'s'[:n^1]} rolled back.")
            return n
        except Exception as e:
            self.logger.error(f"rollback_renamings: {e}")
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
                        "git",  # git fails when launched from a non-versioned directory.
                        "-C",  # This option runs git as if it was started...
                        source.parent,  #  ... in the source's parent directory.
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
            self.logger.info(f"SOURCE:{source}\tTARGET:{target}")
        self.print_arcs(arcs)
        self.print_.newline()

    def print_arcs(self, arcs: List[Arc]):
        previous_parent = Path()
        for (source, target) in arcs:
            if source.parent != previous_parent:
                self.print_.newline()
                self.print_(f"{source.parent}")
                previous_parent = source.parent
            self.print_(f"{source.name} -> {target.name}")
