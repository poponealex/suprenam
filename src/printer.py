import sys
from pathlib import Path

from src.logger import logger


class ColorPrinter:
    """Print colorized messages on the standard output."""

    # Optional ANSI color codes
    OK = "\033[92m"
    WARNING = "\033[1m\033[38;5;166m"
    FAIL = "\033[1m\033[91m"
    RESET = "\033[0m"

    def __call__(self, message: str):
        print(message)

    def newline(self):
        print()

    def success(self, message: str):
        logger.info(f"Success: {message}")
        print(f"{self.OK}Success: {message}{self.RESET}", file=sys.stderr)

    def abort(self, message: str):
        logger.warning(f"Abort: {message}")
        print(f"{self.WARNING}No renamings were performed: {message}{self.RESET}", file=sys.stderr)

    def fail(self, message: str):
        logger.error(f"Fail: {message}")
        print(f"{self.FAIL}Fatal error: {message}{self.RESET}", file=sys.stderr)


class PlatypusPrinter:
    """Print uncolorized messages on the standard output and Platypus' alert."""

    def __init__(self):
        self.buffer = []

    def __call__(self, message: str):
        print(message)

    def newline(self):
        print("\r")

    def success(self, message: str):
        logger.info(f"Success: {message}")
        print(f"ALERT:Success|{message}")

    def abort(self, message: str):
        logger.warning(f"Abort: {message}")
        print(f"ALERT:No renamings were performed|{message}")

    def fail(self, message: str):
        logger.error(f"Fail: {message}")
        print(f"ALERT:Fatal error|{message}")


print_ = ColorPrinter()
if Path.cwd().name == "Resources":
    # We are in the app bundle (macOS)
    print_ = PlatypusPrinter()  # type: ignore
