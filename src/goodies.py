import sys
from pathlib import Path

# logging
LOGGING_FORMAT = "%(asctime)s\n%(levelname)s: %(message)s\n"
LOGGING_DATE_FORMAT = "%d/%m/%Y - %I:%M:%S %p"


# ANSI color codes
OK = "\033[92m"
WARNING = "\033[1m\033[38;5;166m"
FAIL = "\033[1m\033[91m"
INFO = "\033[1;96m"
RESET = "\033[0m"


def print_success(message: str):
    """Print the given message of success."""
    print(f"{OK}{message}{RESET}")


def print_warning(message: str):
    """Print the given message on `sys.stderr`."""
    print(f"{WARNING}Warning: {message}{RESET}", file=sys.stderr)


def print_fail(message: str):
    """Print the given message on `sys.stderr`."""
    print(f"{FAIL}Error: {message}{RESET}", file=sys.stderr)


def print_exit(message: str):
    """Print the given message on `sys.stderr` and exit."""
    sys.exit(f"{FAIL}Error: {message}{RESET}")


def abort_without_renaming(message=None):
    if message:
        print_fail(message)
    print_warning(f"Aborted: no renamings were performed.")


def rm_tree(path: Path): # https://stackoverflow.com/a/57892171/173003
    if not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


from shutil import which


def is_tool(name):  # https://stackoverflow.com/a/34177358/173003
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None
