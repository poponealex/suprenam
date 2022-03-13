import datetime
import logging
import os
import shutil


class Logger:
    def __init__(self, context):
        self.log_dir = context.workspace
        self.path = self.log_dir / "log.txt"
        self.logs_to_keep = context.config.get("logs_to_keep", 10)

    def create_new_log_file(self):
        """Remove all handlers associated with the root logger object and create a NEW log file."""
        self.previous_log_contents = self.get_contents() # used by `get_arcs_for_undoing()`
        self.backup_current_log_file()
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.path, filemode="w", level=logging.DEBUG)

    def backup_current_log_file(self):
        """
        Copy the current log file with a timestamp appended.
        Clean up the directory by keeping only the last self.logs_to_keep copies.
        """
        if self.logs_to_keep == 0:
            return
        try:
            modified = os.path.getmtime(self.path)
        except FileNotFoundError:
            return
        suffix = datetime.datetime.fromtimestamp(modified).strftime("%Y-%m-%d_%H-%M-%S.%f")
        destination = f"{self.path.parent}/log_{suffix}.txt"
        shutil.copy2(self.path, destination)
        for file in sorted(self.log_dir.glob("log_*.txt"), reverse=True)[self.logs_to_keep :]:
            file.unlink()

    def get_contents(self):  # pragma: no cover
        if self.path.is_file():
            return self.path.read_text().strip()
        else:
            return ""

    def warning(self, *args, **kwargs):
        logging.warning(*args, **kwargs)

    def info(self, *args, **kwargs):
        logging.info(*args, **kwargs)

    def error(self, *args, **kwargs):
        logging.error(*args, **kwargs)
