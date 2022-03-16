from pathlib import Path

import pytest

__import__("sys").path[0:0] = "."
from src.get_editable_text import *

data = [  # NB: in the triple-quoted strings, inodes and names are tab-separated.
    (
        "Nothing -> empty result",
        {},
        "",
    ),
    (
        "Empty path -> empty string",
        {
            2612647906: Path(),
        },
        "",
    ),
    (
        "Root -> empty string",
        {
            2612647906: Path("/"),
        },
        "",
    ),
    (
        "A path containing two consecutive '/'",
        {
            2612647906: Path("/foobar//"),
        },
        """
        2612647906	foobar
        """,
    ),
    (
        "A relative path in the current working directory",
        {
            2612647906: Path("foobar"),
        },
        """
        2612647906	foobar
        """,
    ),
    (
        "A path ending with a '/'",
        {
            2612647906: Path("foobar/"),
        },
        """
        2612647906	foobar
        """,
    ),
    (
        "A bunch of siblings -> (unique) parent not displayed",
        {
            2612647906: Path("/usr/lib/gcc-lib"),
            3263123972: Path("/usr/lib/locale"),
            549534358: Path("/usr/lib/X11"),
            1582956841: Path("/usr/lib/tls"),
            1981263235: Path("/usr/lib/games"),
        },
        """
            1981263235	games
            2612647906	gcc-lib
            3263123972	locale
            1582956841	tls
            0549534358	X11
        """,
    ),
    (
        "An arbitrary arborescence -> siblings grouped by parents and sorted",
        {
            1421832123: Path("/usr/bin/X11"),
            2612647906: Path("/usr/lib/gcc-lib"),
            2784148792: Path("/usr/lib"),
            3263123972: Path("/usr/lib/locale"),
            1482466386: Path("/usr/bin"),
            549534358: Path("/usr/lib/X11"),
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
            1981263235	games
            2612647906	gcc-lib
            3263123972	locale
            1582956841	tls
            0549534358	X11
        """,
    ),
    (
        "A bunch of siblings （shown in default order) -> names sorted in natural order",
        {
            1421832123: Path("/usr/lib/Apple"),
            2612647906: Path("/usr/lib/apple14,689"),
            2784148792: Path("/usr/lib/apple15"),
            1482466380: Path("/usr/lib/Banana_b"),
            3263123972: Path("/usr/lib/banana_a"),
            1482466386: Path("/usr/lib/banana_d"),
            1482466387: Path("/usr/lib/bâñáñà_c"),
            549534358: Path("/usr/lib/version-1.10"),
            1582956841: Path("/usr/lib/version-1.11"),
            1981263235: Path("/usr/lib/version-1.9"),
            1981263299: Path("/usr/lib/version-2.0"),
        },
        """
            1421832123	Apple
            2612647906	apple14,689
            2784148792	apple15
            3263123972	banana_a
            1482466380	Banana_b
            1482466387	bâñáñà_c
            1482466386	banana_d
            1981263235	version-1.9
            0549534358	version-1.10
            1582956841	version-1.11
            1981263299	version-2.0
        """,
    ),
    (
        "The parents are also sorted in natural order",
        {
            1482466380: Path("/usr/Banana_b/foobar"),
            3263123972: Path("/usr/banana_a/foobar"),
            1482466386: Path("/usr/banana_c/foobar"),
        },
        """
        /usr/banana_a
        3263123972	foobar

        /usr/Banana_b
        1482466380	foobar

        /usr/banana_c
        1482466386	foobar
        """,
    ),
]


@pytest.mark.parametrize("title, inodes_paths, expected", data)
def test_get_editable_text(title, inodes_paths, expected):
    print(title)
    expected = expected.strip().replace("    ", "").split("\n")
    result = get_editable_text(inodes_paths).strip().split("\n")
    print("\n".join(result))
    assert len(expected) == len(result)
    for (expected_line, result_line) in zip(expected, result):
        assert expected_line == result_line




if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
