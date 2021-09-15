from pathlib import Path

import context
from src.edition import *

import pytest

editable_text_dataset = [  # NB: in the triple-quoted strings, inodes and names are tab-separated.
    # Rename nothing -> empty result (TODO check if this case can occur or is filtered out before)
    (
        {},
        "",
    ),
    # Rename empty path -> empty string (TODO check if this case can occur or is filtered out before)
    (
        {
            2612647906: Path(),
        },
        """
            2612647906	
        """,
    ),
    # Rename root -> empty string (TODO check if this case can occur or is filtered out before)
    (
        {
            2612647906: Path("/"),
        },
        """
            2612647906	
        """,
    ),
    # Rename a bunch of siblings -> their (unique) parent is not displayed
    (
        {
            2612647906: Path("/usr/lib/gcc-lib"),
            3263123972: Path("/usr/lib/locale"),
            1549534358: Path("/usr/lib/X11"),
            1582956841: Path("/usr/lib/tls"),
            1981263235: Path("/usr/lib/games"),
        },
        """
            1549534358	X11
            1981263235	games
            2612647906	gcc-lib
            3263123972	locale
            1582956841	tls
        """,
    ),
    # Rename an arbitrary arborescence -> the siblings are grouped by parents, and sorted
    (
        {
            1421832123: Path("/usr/bin/X11"),
            2612647906: Path("/usr/lib/gcc-lib"),
            2784148792: Path("/usr/lib"),
            3263123972: Path("/usr/lib/locale"),
            1482466386: Path("/usr/bin"),
            1549534358: Path("/usr/lib/X11"),
            1582956841: Path("/usr/lib/tls"),
            1981263235: Path("/usr/lib/games"),
        },
        """
            /usr
            1482466386	bin
            2784148792	lib
    
            /usr/bin
            1421832123	X11
    
            /usr/lib
            1549534358	X11
            1981263235	games
            2612647906	gcc-lib
            3263123972	locale
            1582956841	tls
        """,
    ),
]


@pytest.mark.parametrize("inode_paths, expected", editable_text_dataset)
def test_get_editable_text(inode_paths, expected):
    expected = expected.strip().replace("    ", "").split("\n")
    result = get_editable_text(inode_paths).strip().split("\n")
    assert len(expected) == len(result)
    for (expected_line, result_line) in zip(expected, result):
        assert expected_line == result_line


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
