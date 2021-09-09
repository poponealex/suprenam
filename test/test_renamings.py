
from pathlib import Path

import context
from src.renamings import *
from src.user_types import Renaming

import pytest

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
    renamings = [
        Renaming(base / "source_1", base / "target_1"),
        Renaming(base / "source_2", base / "target_2"),
        Renaming(base / "source_3", base / "target_3"),
    ]
    for renaming in renamings:
        renaming.source.touch()
    set_logger(Path("test/happy_log.txt"))
    perform_renamings(renamings)
    try:
        assert set(base.iterdir()) == set(renaming.target for renaming in renamings)
        # TODO: uncomment the following lines and try to understand why no logging file
        #       is created when launched by pytest.
        # undo_renamings(Path("test/happy_log.txt"))
        # assert set(base.iterdir()) == set(renaming.source for renaming in renamings)
    finally:
        rm_tree(base)
    

def test_rollback_path():
    """Test the case where a renaming fails, and the previous ones are reverted."""
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    renamings = [
        Renaming(base / "source_1", base / "target_1"),
        Renaming(base / "source_2", base / "target_2"),
        Renaming(base / "source_3", base / "target_3"),
        Renaming(base / "source_4", base / "target_4"),
    ]
    for renaming in renamings:
        renaming.source.touch()
    renamings[2].source.unlink() # delete a source
    set_logger(Path("test/rollback_log.txt"))
    with pytest.raises(SystemExit):
        perform_renamings(renamings)
    try:
        assert set(base.iterdir()) == {base / "source_1", base / "source_2", base / "source_4"}
    finally:
        rm_tree(base)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
