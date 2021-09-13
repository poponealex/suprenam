import pytest

from pathlib import Path

import context
from src.suprenam import *
from test_renamings import rm_tree


def test_get_text():
    base = Path("test") / "temp"
    rm_tree(base)
    base.mkdir()
    parent = Path.cwd() / "test" / "temp"
    paths = [base / "foo", base / "bar", base / "spam"]
    for path in paths:
        path.touch()
    actual = get_text(paths)
    expected = f"{parent}\n\n{paths[0].stat().st_ino}\tfoo\n{paths[1].stat().st_ino}\tbar\n{paths[2].stat().st_ino}\tspam\n"
    print(expected)
    assert actual == expected
    rm_tree(base)


def test_parse_temporary_file():
    base = Path("test") / "temp"
    rm_tree(base)
    base.mkdir()
    parent = Path.cwd() / "test" / "temp"
    paths = [base / "foo", base / "bar", base / "spam"]
    for path in paths:
        path.touch()
    population = {path.stat().st_ino: path for path in paths}
    temp_file = Path(base) / "temp.txt"
    temp_file.touch()
    temp_file.write_text(f"{parent}\n\n{paths[0].stat().st_ino}\tfoo\n{paths[1].stat().st_ino}\tbar\n{paths[2].stat().st_ino}\tspam\n")
    actual = parse_temporary_file(temp_file, population)
    expected = [Clause(paths[0], "foo"), Clause(paths[1], "bar"), Clause(paths[2], "spam")]
    assert actual == expected
    rm_tree(base)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
