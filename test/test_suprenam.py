import pytest

from pathlib import Path

import context
from src.suprenam import *
from test_renamings import rm_tree


@pytest.fixture(scope="module")
def paths():
    return [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]


@pytest.fixture(scope="module")
def inodes(paths):
    return {path: i for (i, path) in enumerate(paths)}


def test_get_text():
    base = Path("/Users/bob/")
    paths = [base / "foo", base / "bar", base / "spam"]
    inodes = {path: i for (i, path) in enumerate(paths)}
    actual = get_text(paths, get_inode=lambda path: inodes[path])
    expected = f"{base}\n\n0\tfoo\n1\tbar\n2\tspam\n"
    assert actual == expected


def test_parse_text(paths, inodes):
    population = {i: path for (i, path) in enumerate(paths)}
    text = get_text(paths, get_inode=lambda path: inodes[path])
    actual = set(parse_text(text, population))
    expected = set(map(lambda path: Clause(path, path.name), paths))
    assert actual == expected


def test_edit_paths(paths, inodes):
    get_inode = lambda path: inodes[path]
    suffix = "_edit"
    new_paths = [*map(lambda path: path.with_name(path.name + suffix), paths)]
    actual = set(
        edit_paths(
            paths,
            get_inode=get_inode,
            create_temporary_file=lambda _: get_text(paths, get_inode),
            get_edition_handler=lambda text: "\n".join(map(lambda line: line + suffix, text.split("\n"))),
            edit=lambda _: None,
            handler=lambda _: None,
        )
    )
    expected = set(map(lambda path: Clause(path, path.name + suffix), paths))
    assert actual == expected


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
