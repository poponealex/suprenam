from pathlib import Path
from typing import List

from src.user_types import Inode, InodesPaths


def paths_to_inodes_paths(paths: List[Path]) -> InodesPaths:
    """
    Given a list of paths, return a mapping from inodes to paths.

    Args:
        paths: list of Path objects
    
    Raises:
        FileNotFoundError: if any of the paths does not exist.

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
        raise FileNotFoundError(f"The following items are missing: {missing_paths}.")
    else:    
        return result
