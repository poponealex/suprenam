from pathlib import Path
from typing import List

from src.user_errors import NoItemToRenameError
from src.user_types import Inode, InodesPaths


def paths_to_inodes_paths(paths: List[Path]) -> InodesPaths:
    """
    Given a list of paths, return a mapping from inodes to paths.

    Args:
        paths: list of Path objects

    Raises:
        FileNotFoundError: if any of the paths does not exist.
        NoItemToRenameError: empty single text file as a command-line argument.

    Returns:
        A mapping from inodes to paths.
    """
    result = {}
    missing_paths = []
    for path in paths:
        if path.exists():
            result[Inode(path.stat().st_ino)] = path
        else:
            missing_paths.append(path)
    if missing_paths:
        n = len(missing_paths)
        raise FileNotFoundError(f"{n} missing item{'s'[:n^1]}: {list(map(str,missing_paths))}.")
    elif not result:
        raise NoItemToRenameError("No item to rename was provided.")
    else:
        return result
