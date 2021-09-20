from pathlib import Path

import context
from src.edition import *

import pytest

editable_text_dataset = [  # NB: in the triple-quoted strings, inodes and names are tab-separated.
    (
        "Rename nothing -> empty result (TODO check if this case can occur or is filtered out before)",
        {},
        "",
    ),
    (
        "Rename empty path -> empty string (TODO check if this case can occur or is filtered out before)",
        {
            2612647906: Path(),
        },
        """
            2612647906	
        """,
    ),
    (
        "Rename root -> empty string (TODO check if this case can occur or is filtered out before)",
        {
            2612647906: Path("/"),
        },
        """
            2612647906	
        """,
    ),
    (
        "Rename a bunch of siblings -> their (unique) parent is not displayed",
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
    (
        "Rename an arbitrary arborescence -> the siblings are grouped by parents, and sorted",
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


@pytest.mark.parametrize("title, inode_paths, expected", editable_text_dataset)
def test_get_editable_text(title, inode_paths, expected):
    print(title)
    expected = expected.strip().replace("    ", "").split("\n")
    result = get_editable_text(inode_paths).strip().split("\n")
    assert len(expected) == len(result)
    for (expected_line, result_line) in zip(expected, result):
        assert expected_line == result_line


edited_text_dataset = [
    (
        "Parse a file which doesn't end with a newline.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foobar
            456	club""",
        [
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which is missing an inode.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            	foobar
            456	club
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which is missing multiple inodes.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            	foobar
            	club
        """,
        [],
    ),
    (
        "Parse a file which is missing a name.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	
            456	club
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which is missing multiple names.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	
            456	
        """,
        [],
    ),
    (
        "Parse a file which contains a name made of whitespaces.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	    
            456	club
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains a line with multiple tabs.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123				foobar
            456	club
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains a name that is only digits.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	12345
            456	club
        """,
        [
            Clause(Path("/home/foo"), "12345"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains too many inodes (superset).",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foobar
            456	club
            789 spam
        """,
        [
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which doesn't contain all the inodes (subset).",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foobar
        """,
        [
            Clause(Path("/home/foo"), "foobar"),
        ],
    ),
    (
        "Parse a file which only contains different inodes from the original ones (symmetric difference).",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
            789: Path("/home/spam"),
        },
        """
            1234	foobar
            4567	club
            7890	spam
        """,
        [],
    ),
    (
        "Parse a file which doesn't contain any modification.",
        {123: Path("/home/foo"), 456: Path("/home/bar")},
        """
            123	foo
            456	bar
        """,
        [],
    ),
    (
        "Parse a file which is empty.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        "",
        [],
    ),
    (
        "Parse a file which doesn't contain any errors.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foobar
            456	club
        """,
        [
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains paths with different parents.",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
            789: Path("/etc/lib"),
            999: Path("/hello/world"),
        },
        """
            /home
            123	foobar
            456	club

            /etc
            789	book

            /hello
            999	moon
        """,
        [
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/bar"), "club"),
            Clause(Path("/etc/lib"), "book"),
            Clause(Path("/hello/world"), "moon"),
        ],
    ),
]


@pytest.mark.parametrize("title, inode_paths, text, expected", edited_text_dataset)
def test_parse_edited_text(title, inode_paths, text, expected):
    print(title)
    text = "\n".join(line.strip() for line in text.split("\n"))
    actual = parse_edited_text(text, inode_paths)
    assert actual == expected


@pytest.mark.parametrize("title, inode_paths, text, expected", edited_text_dataset)
def test_edit_paths(title, inode_paths, text, expected):
    print(title)
    actual = edit_paths(
        paths=inode_paths.values(),
        get_inode=lambda x: {path: inode for (inode, path) in inode_paths.items()}[x],
        get_edition_handler=lambda _: None,
        edit=lambda _: "\n".join(line.strip() for line in text.split("\n")),
    )
    assert actual == expected


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
