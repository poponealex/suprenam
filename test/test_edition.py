from pathlib import Path

import context
from src.edition import *

import pytest


def test_get_editable_text():
    inode_paths = {
        1421832123: Path("/usr/bin/X11"),
        2612647906: Path("/usr/lib/gcc-lib"),
        2784148792: Path("/usr/lib"),
        3263123972: Path("/usr/lib/locale"),
        482466386: Path("/usr/bin"),
        549534358: Path("/usr/lib/X11"),
        582956841: Path("/usr/lib/tls"),
        981263235: Path("/usr/lib/games"),
    }
    expected = """
        /usr
        482466386	bin
        2784148792	lib

        /usr/bin
        1421832123	X11

        /usr/lib
        549534358	X11
        981263235	games
        2612647906	gcc-lib
        3263123972	locale
        582956841	tls
    """  # NB: inodes and paths are tab-separated
    expected = expected.strip().replace("    ", "").split("\n")
    result = get_editable_text(inode_paths).strip().split("\n")
    assert len(expected) == len(result)
    for (expected_line, result_line) in zip(expected, result):
        assert expected_line == result_line


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
