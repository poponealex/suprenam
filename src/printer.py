import sys
from pathlib import Path


class Printer:

    def __init__(self, context):
        self.logger = context.logger
        if Path.cwd().name == "Resources": # We are in the app bundle (macOS)
            # Print uncolorized messages in Platypus' alert.
            def print_to_platypus(title, text):
                print(f"ALERT: {title}|{text}")
            self.print_success = lambda text: print_to_platypus("Success", text)
            self.print_abort = lambda text: print_to_platypus("No renamings", text)
            self.print_fail = lambda text: print_to_platypus("Fatal error", text)
            self.newline = lambda: print()
        else:
            # Print colorized messages on the standard error.
            self.OK = "\033[92m"
            self.WARNING = "\033[1m\033[38;5;166m"
            self.FAIL = "\033[1m\033[91m"
            self.RESET = "\033[0m"
            def print_to_stderr(ansi_markup, title, text):
                print(f"{ansi_markup}{title}: {text}{self.RESET}", file=sys.stderr)
            self.print_success = lambda text: print_to_stderr(self.OK, "Success", text)
            self.print_abort = lambda text: print_to_stderr(self.WARNING, "No renamings", text)
            self.print_fail = lambda text: print_to_stderr(self.FAIL, "Fatal error", text)
            self.newline = lambda: print("\r")

    def __call__(self, message: str):
        print(message)

    def success(self, message: str):
        self.logger.info(f"Success: {message}")
        self.print_success(message)

    def abort(self, message: str):
        self.logger.warning(f"Abort: {message}")
        self.print_abort(message)

    def fail(self, message: str):
        self.logger.error(f"Fail: {message}")
        self.print_fail(message)

