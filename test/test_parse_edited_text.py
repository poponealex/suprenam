import re
from pathlib import Path

import pytest
from pathvalidate import ValidationError

__import__("sys").path[0:0] = "."
from src.parse_edited_text import *

data = [
    (
        "Parse a file which doesn't end with a newline.",
        ["universal"],
        "no_exception",
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
        ["universal"],
        "no_exception",
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
        "Parse a file which contains a name starting with a space.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	 foobar
            456	club
        """,
        [
            Clause(Path("/home/foo"), " foobar"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains a name made of multiple whitespaces.",
        ["macOS", "Linux"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	    
            456	club
        """,
        [
            Clause(Path("/home/foo"), "    "),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains an inode preceeded by a whitespace.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
             123	foobar
            456	club
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains a name containing a '\\' character on macOS/Linux.",
        ["macOS", "Linux"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foo\\bar
            456	club
        """,
        [
            Clause(Path("/home/foo"), "foo\\bar"),
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which contains a name containing a '\\' character on Windows.",
        ["Windows"],
        ValidationError,
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foo\\bar
            456	club
        """,
        [],
    ),
    (
        "Parse a file which contains a name that is only digits.",
        ["universal"],
        "no_exception",
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
        ["universal"],
        "no_exception",
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
        ["universal"],
        "no_exception",
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
        "Parse a file which contains only one modification.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
            789: Path("/home/spam"),
        },
        """
            123	foo
            456	club
            789	spam
        """,
        [
            Clause(Path("/home/bar"), "club"),
        ],
    ),
    (
        "Parse a file which doesn't contain any modification.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        """
            123	foo
            456	bar
        """,
        [],
    ),
    (
        "Parse a file which is empty.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
            456: Path("/home/bar"),
        },
        "",
        [],
    ),
    (
        "Parse a file which contains paths with different parents.",
        ["universal"],
        "no_exception",
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
    (
        "Parse a file which is missing a name.",
        ["universal"],
        EmptyNameError,
        {
            123: Path("/home/foo"),
        },
        """
            123	
        """,
        [],
    ),
    (
        "Parse a file which contains an illegal '/' character.",
        ["universal"],
        ValidationError,
        {
            123: Path("/home/foo"),
        },
        """
            123	foo/bar
        """,
        [],
    ),
    (
        "Parse a file whose name refers to the parent directory.",
        ["universal"],
        ValidationError,
        {
            123: Path("/home/foo"),
        },
        """
            123	../foo
        """,
        [],
    ),
    (
        "Parse a file which contains a non-existent inode.",
        ["universal"],
        UnknownInodeError,
        {
            123: Path("/home/foo"),
        },
        """
            222	foobar
        """,
        [],
    ),
    (
        "Parse a file which contains multiple tabs in between the inode and the new name.",
        ["universal"],
        TabulationError,
        {
            123: Path("/home/foo"),
        },
        """
            123				foobar
        """,
        [],
    ),
    (
        "Parse a file which contains several times the same inode with different targets.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
        },
        """
            123	foobar
            123	barfoo
        """,
        [ # This case will be filtered out by secure_clauses().
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/foo"), "barfoo"),
        ],
    ),
    (
        "Parse a file which contains several times the same inode with the same target.",
        ["universal"],
        "no_exception",
        {
            123: Path("/home/foo"),
        },
        """
            123	foobar
            123	foobar
        """,
        [ # This case will be filtered out by secure_clauses().
            Clause(Path("/home/foo"), "foobar"),
            Clause(Path("/home/foo"), "foobar"),
        ],
    ),
    (
        "Parse a file which contains some numerical parents.",
        ["universal"],
        "no_exception",
        {
            123: Path("321/foo"),
            456: Path("321/bar"),
            789: Path("654/lib"),
            999: Path("987/world"),
        },
        """
            321
            123	foobar
            456	club

            654
            789	book

            987
            999	moon
        """,
        [
            Clause(Path("321/foo"), "foobar"),
            Clause(Path("321/bar"), "club"),
            Clause(Path("654/lib"), "book"),
            Clause(Path("987/world"), "moon"),
        ],
    ),
]


split_startwith_tabs = re.compile(r"(?m)^([ ]{4})*(.*)$").findall


@pytest.mark.parametrize("title, platforms, exception, inodes_paths, text, expected", data)
def test_parse_edited_text(title, platforms, exception, inodes_paths, text, expected):
    print(title)
    text = "\n".join(line for (_, line) in split_startwith_tabs(text))
    for platform in platforms:
        actual = lambda: parse_edited_text(text, inodes_paths, platform)
        if exception != "no_exception":
            with pytest.raises(exception):
                actual()
        else:
            print(actual())
            print(expected)
            assert actual() == expected


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
