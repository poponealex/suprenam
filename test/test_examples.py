import pytest

from pathlib import Path

import context
import src.secure_clauses as sc
from src.file_system import FileSystem
from extract_examples import extract_examples
from reformat_examples import main as reformat_examples

EXCEPTIONS = {
    "FileNotFoundError": __builtins__["FileNotFoundError"],
    "SeveralTargetsError": getattr(sc, "SeveralTargetsError"),
    "SeveralSourcesError": getattr(sc, "SeveralSourcesError"),
    "DuplicatedClauseError": getattr(sc, "DuplicatedClauseError"),
}

PATHS = [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]
EXAMPLES_MD_PATH = Path("test/examples.md")

reformat_examples(EXAMPLES_MD_PATH)


@pytest.mark.parametrize(
    "i, title, example, expected",
    [d.values() for d in extract_examples(EXAMPLES_MD_PATH)[:]],
)
def test(i, title, example, expected):
    clauses = [(Path(row[0]), row[1]) for row in example]
    fs = FileSystem(PATHS)
    original_fs = set(fs)
    if isinstance(expected, tuple):
        (exception_name, expected_culprit) = expected
        with pytest.raises(EXCEPTIONS[exception_name]) as culprit:
            sc.secure_clauses(fs, clauses)
        assert culprit.value.args[0] == expected_culprit
        assert fs == original_fs
    else:
        safe_clauses = sc.secure_clauses(fs, clauses)
        additions = {Path(row[1]) for row in expected}
        deletions = {Path(row[0]) for row in expected}
        (additions, deletions) = (additions - deletions, deletions - additions)
        assert original_fs - fs == deletions
        assert fs - original_fs == additions


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
