import pytest

from pathlib import Path

import context
from src.renamer import rename
from src.file_system import FileSystem
from extract_examples import extract_examples


PATHS = [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]


@pytest.mark.parametrize(
    "i, title, example, expected",
    [d.values() for d in extract_examples(Path("test/examples.md"))],
)
def test(i, title, example, expected):
    clauses = [(Path(row[0]), row[1]) for row in example]
    fs = FileSystem(PATHS)
    original_fs = set(fs)
    rename(clauses, fs)
    additions = {Path(row[1]) for row in expected}
    deletions = {Path(row[0]) for row in expected}
    (additions, deletions) = (additions - deletions, deletions - additions)
    assert original_fs - fs == deletions
    assert fs - original_fs == additions


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
