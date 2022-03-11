from pathlib import Path

import pytest

__import__("sys").path[0:0] = "."
from src.paths_to_inodes_paths import *


def test_existing_paths_to_inodes_paths():
    paths = [  # eat your own dog food
        Path("src/paths_to_inodes_paths.py"),
        Path("test/test_paths_to_inodes_paths.py"),
    ]
    result = paths_to_inodes_paths(paths)
    assert all(isinstance(inode, int) for inode in result.keys())
    assert set(result.values()) == set(paths)


def test_non_existing_paths_to_inodes_paths():
    paths = [
        Path("src/paths_to_inodes_paths.py"),
        Path("missing_file_1.txt"),
        Path("missing_file_2.txt"),
    ]
    with pytest.raises(FileNotFoundError):
        paths_to_inodes_paths(paths)


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
