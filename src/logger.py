import datetime
import logging
import os
import shutil
from pathlib import Path


class Logger:

    LOG_DIR = Path.home() / ".suprenam"
    LOG_NAME = "log.txt"
    LOGS_TO_KEEP = 10

    def __init__(self, path: Path = LOG_DIR / LOG_NAME):
        """Ensure the log directory exists."""
        path.parent.mkdir(
            parents=True,  # any missing parents of this path are created as needed
            exist_ok=True,  # if the directory already exists, do not raise an exception
        )
        self.path = path

    def create_new_log_file(self):
        """Remove all handlers associated with the root logger object and create a NEW log file."""
        self.backup_current_log_file()
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.path, filemode="w", level=logging.DEBUG)

    def backup_current_log_file(self):
        """
        Copy the current log file with a timestamp appended.
        Clean up the directory by keeping only the last copies.
        """
        if self.LOGS_TO_KEEP == 0:
            return
        try:
            modified = os.path.getmtime(self.path)
        except FileNotFoundError:
            return
        suffix = datetime.datetime.fromtimestamp(modified).strftime("%Y-%m-%d_%H-%M-%S.%f")
        destination = f"{self.path.parent}/log_{suffix}.txt"
        shutil.copy2(self.path, destination)
        for file in sorted(self.LOG_DIR.glob("log_*.txt"), reverse=True)[self.LOGS_TO_KEEP :]:
            file.unlink()

    def get_contents(self):  # pragma: no cover
        if self.path.is_file():
            return self.path.read_text().strip()
        else:
            return ""

    def erase_contents(self):
        self.path.write_text("")

    def warning(self, *args, **kwargs):
        logging.warning(*args, **kwargs)

    def info(self, *args, **kwargs):
        logging.info(*args, **kwargs)

    def error(self, *args, **kwargs):
        logging.error(*args, **kwargs)


logger = Logger()
