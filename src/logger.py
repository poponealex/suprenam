import logging
from pathlib import Path


class Logger:

    LOG_DIR = Path.home() / ".suprenam"
    LOG_NAME = "log.txt"

    def __init__(self, path: Path = LOG_DIR / LOG_NAME):
        """Create a log file at the specified path."""
        # Ensure the log directory exists.
        path.parent.mkdir(
            parents=True,  # any missing parents of this path are created as needed
            exist_ok=True,  # if the directory already exists, do not raise an exception
        )
        self.path = path

    def create_new_log_file(self):
        """Remove all handlers associated with the root logger object and create a NEW log file."""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.path, filemode="w", level=logging.DEBUG)

    def get_contents(self):  # pragma: no cover
        return self.path.read_text().strip()
    
    def erase_contents(self):
        self.path.write_text("")
    
    def warning(self, *args, **kwargs):
        logging.warning(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        logging.info(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        logging.error(*args, **kwargs)
    

logger = Logger()