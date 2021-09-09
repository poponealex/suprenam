import pytest

from pathlib import Path

import context
from src.renamings import perform_renamings


def rm_tree(path: Path):  # https://stackoverflow.com/a/57892171/173003
    if not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def test_happy_path():
    """Test the case where all the renamings succeed."""
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    source_paths = [
        base / "source_1",
        base / "source_2",
        base / "source_3",
    ]
    for source_path in source_paths:
        source_path.touch()
    target_names = [
        "target_1",
        "target_2",
        "target_3",
    ]
    perform_renamings(zip(source_paths, target_names), "log.txt")
    try:
        assert {path.name for path in base.iterdir()} == set(target_names)
    finally:
        rm_tree(base)

def test_rollback_path():
    """Test the case where a renaming fails, and the previous ones are reverted."""
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    source_paths = [
        base / "source_1",
        base / "source_2",
        base / "source_3", # to be deleted
        base / "source_4",
    ]
    for source_path in source_paths:
        source_path.touch()
    (base / "source_3").unlink()
    target_names = [
        "target_1",
        "target_2",
        "target_3",
        "target_4",
    ]
    with pytest.raises(SystemExit):
        perform_renamings(zip(source_paths, target_names), "log.txt")
    try:
        assert {path.name for path in base.iterdir()} == {"source_1", "source_2", "source_4"}
    finally:
        rm_tree(base)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
