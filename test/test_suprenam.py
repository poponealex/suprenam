import pytest

from pathlib import Path

import context
from src.suprenam import *
from test_renamings import rm_tree


def test_get_text():
    paths = [Path("/Users/bob/foo"), Path("/Users/bob/bar"), Path("/Users/bob/spam")]
    expected = "/Users/bob\n\n0\tfoo\n1\tbar\n2\tspam\n"
    actual = get_text(paths, get_inode=lambda path: paths.index(path))
    assert actual == expected


def test_parse_text():
    paths = [Path("/Users/bob/foo"), Path("/Users/bob/bar"), Path("/Users/bob/spam")]
    expected = [Clause(Path("/Users/bob/foo"), "foo"), Clause(Path("/Users/bob/bar"), "bar"), Clause(Path("/Users/bob/spam"), "spam")]
    text = get_text(paths, get_inode=lambda path: paths.index(path))
    actual = parse_text(text, {inode: path for (inode, path) in enumerate(paths)})
    assert set(actual) == set(expected)


def test_edit_paths():
    paths = [Path("/Users/bob/foo"), Path("/Users/bob/bar"), Path("/Users/bob/spam")]
    renamings = "0\tboo\n1\ttar\n2\tbam"
    expected = [Clause(Path("/Users/bob/foo"), "boo"), Clause(Path("/Users/bob/bar"), "tar"), Clause(Path("/Users/bob/spam"), "bam")]
    get_inode = lambda path: paths.index(path)
    actual = edit_paths(
        paths,
        get_inode=get_inode,
        create_temporary_file=lambda _: get_text(paths, get_inode),
        get_edition_handler=lambda text: renamings,
        edit=lambda _: None,
        handler=lambda _: None,
    )
    assert set(actual) == set(expected)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
