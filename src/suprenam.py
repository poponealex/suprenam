import re
import subprocess, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from itertools import groupby
from pathlib import Path
from platform import platform
from tempfile import NamedTemporaryFile
from typing import List

from src.file_system import FileSystem
from src.goodies import *
from src.renamings import perform_renamings, undo_renamings, set_logger
from src.secure_clauses import secure_clauses


LOG_DIR = Path.cwd() / ".suprenam"
LOG_NAME = "previous_session.log"


def main():
    args = cli_arguments()
    paths = []
    if args.undo:
        return undo_renamings(LOG_DIR / LOG_NAME)
    if args.paths:
        paths += [*map(lambda x: Path(x), args.paths)]
    if args.file:
        paths += [Path(path) for path in Path(args.file).read_text().split("\n") if path]
    if not paths:
        return print_warning("No paths were provided.")
    create_log()
    file_system = FileSystem([])
    renamings = secure_clauses(file_system, edit_paths(paths))
    return perform_renamings(renamings)


def cli_arguments():
    """
    CLI argument parser.

    Returns:
        `parser.parse_args()` dict containing the parsed arguments.
    """
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        usage=f"\n{WARNING}suprenam.py [-p paths] [-f file] [-h help]{RESET}",
        description=f"{OK}\nFILE RENAMER{RESET}",
    )

    parser.add_argument(
        "-p",
        "--paths",
        nargs="+",
        help=f"{OK}The paths you want to rename.{RESET}",
        action="store",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=f"{OK}Parse paths stored in a file (newline separated).{RESET}",
        action="store",
    )

    parser.add_argument(
        "-u",
        "--undo",
        help=f"{OK}Undo completed renamings from the previous session.{RESET}",
        action="store",
    )

    return parser.parse_args()


def create_log():
    if not LOG_DIR.exists():
        LOG_DIR.mkdir()
    return set_logger(LOG_DIR / LOG_NAME)


if __name__ == "__main__":
    sys.exit(main())
