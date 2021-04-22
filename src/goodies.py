import sys

# ANSI color codes
OK = "\033[92m"
WARNING = "\033[1m\033[38;5;166m"
FAIL = "\033[1m\033[91m"
RESET = "\033[0m"


def print_success(message: str):
    """Print the given message of success."""
    print(f"{OK}{message}{RESET}")


def print_warning(message: str):
    """Print the given message on `sys.stderr`."""
    print(f"{WARNING}Warning: {message}{RESET}", file=sys.stderr)


def print_fail(message: str):
    """Print the given message on `sys.stderr` and raise a ValueError."""
    print(f"{FAIL}Error: {message}{RESET}", file=sys.stderr)
    raise ValueError(message)


def print_exit(message: str):
    """Print the given message on `sys.stderr` and exit."""
    sys.exit(f"{FAIL}Error: {message}{RESET}")


from shutil import which

def is_tool(name): # https://stackoverflow.com/a/34177358/173003
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None
