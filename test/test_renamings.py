
from pathlib import Path

import context
from src.renamings import *
from src.user_types import Arc
from src.goodies import rm_tree

import pytest


def test_happy_path():
    """Test the case where all the arcs succeed."""
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
        Arc(base / "source_3", base / "target_3"),
    ]
    for arc in arcs:
        arc.source.touch()
    perform_renamings(arcs, Path("test/happy_log.txt"))
    try:
        assert set(base.iterdir()) == set(arc.target for arc in arcs)
        # TODO: uncomment the following lines and try to understand why no logging file
        #       is created when launched by pytest.
        # undo_arcs(Path("test/happy_log.txt"))
        # assert set(base.iterdir()) == set(arc.source for arc in arcs)
    finally:
        rm_tree(base)
    

def test_rollback_path():
    """Test the case where a renaming fails, and the previous ones are reverted."""
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
        Arc(base / "source_3", base / "target_3"),
        Arc(base / "source_4", base / "target_4"),
    ]
    for arc in arcs:
        arc.source.touch()
    arcs[2].source.unlink() # delete a source
    with pytest.raises(SystemExit):
        perform_renamings(arcs, Path("test/rollback_log.txt"))
    try:
        assert set(base.iterdir()) == {base / "source_1", base / "source_2", base / "source_4"}
    finally:
        rm_tree(base)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
