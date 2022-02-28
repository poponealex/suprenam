import sys
from pathlib import Path


class ColorPrinter:
    """Print colorized messages on the standard output."""

    # Optional ANSI color codes
    OK = "\033[92m"
    WARNING = "\033[1m\033[38;5;166m"
    FAIL = "\033[1m\033[91m"
    INFO = "\033[1;96m"
    RESET = "\033[0m"

    def __call__(self, message: str):
        print(message)

    def newline(self):
        print()

    def success(self, message: str):
        print(f"{self.OK}Success: {message}{self.RESET}")

    def warning(self, message: str):
        print(f"{self.WARNING}Warning: {message}{self.RESET}", file=sys.stderr)

    def fail(self, message: str):
        print(f"{self.FAIL}Error: {message}{self.RESET}", file=sys.stderr)

    def no_renamings(self, message=None):
        if message:
            self.fail(message)
        print(f"{self.WARNING}Aborted: no renamings were performed.{self.RESET}")


class PlatypusPrinter:
    """Print uncolorized messages on the standard output."""

    def __init__(self):
        self.buffer = []

    def __call__(self, message: str):
        print(message)

    def newline(self):
        print("\r")

    def success(self, message: str):
        print(f"ALERT:Success|{message}")

    def warning(self, message: str):
        print(f"ALERT:Warning|{message}")

    def fail(self, message: str):
        print(f"ALERT:Error|{message}")

    def no_renamings(self, message=None):
        print("Aborted: no renamings were performed.")
        if message:
            self.fail(message)


print_ = ColorPrinter()
if Path.cwd().name == "Resources":
    # We are in the app bundle (macOS)
    print_ = PlatypusPrinter()  # type: ignore
