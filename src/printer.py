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

    def flush_buffer_and_exit(self):
        pass  # ignored


class PlatypusPrinter:
    """Print uncolorized messages on the standard output."""

    def __init__(self):
        self.buffer = []

    def __call__(self, message: str):
        print(message)

    def newline(self):
        print("\r")

    def success(self, message: str):
        self.buffer.append(f"Success: {message}")

    def warning(self, message: str):
        self.buffer.append(f"Warning: {message}")

    def fail(self, message: str):
        self.buffer.append(f"Error: {message}")

    def no_renamings(self, message=None):
        if message:
            self.fail(message)
        self.buffer.append("Aborted: no renamings were performed.")

    def flush_buffer_and_exit(self):
        title = self.buffer.pop()
        message = "\n".join(self.buffer)
        print("NOTIFICATION:title|message\n")
        print("QUITAPP\n")


print_ = ColorPrinter()
if Path.cwd().name == "Resources":
    # We are in the app bundle (macOS)
    PlatypusPrinter()  # type: ignore