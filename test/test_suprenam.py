import pytest

from pathlib import Path

import context
from src.suprenam import *
from test_renamings import rm_tree
from src.user_types import Clause


def test_temporary_file():
    base = Path("test") / "temp"
    rm_tree(base)
    base.mkdir()
    parent = Path.cwd() / "test" / "temp"
    paths = [base / "foo", base / "bar", base / "spam"]
    for path in paths:
        path.touch()
    population = {path.stat().st_ino: path for path in paths}
    temp_file = create_temporary_file(paths)
    expected = f"{parent}\n\n{paths[0].stat().st_ino}\tfoo\n{paths[1].stat().st_ino}\tbar\n{paths[2].stat().st_ino}\tspam\n"
    print(temp_file.read_text())
    assert expected == temp_file.read_text()
    temp_file.write_text(f"{parent}\n\n{paths[0].stat().st_ino}\tboo\n{paths[1].stat().st_ino}\ttar\n{paths[2].stat().st_ino}\tbam\n")
    expected = [Clause(paths[0], "boo"), Clause(paths[1], "tar"), Clause(paths[2], "bam")]
    actual = parse_temporary_file(temp_file, population)
    assert actual == expected
    rm_tree(base)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
