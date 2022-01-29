from pathlib import Path

import context
from src.renamings import *
from src.user_types import Arc
from src.goodies import rm_tree

import pytest


def test_rename():
    """All renamings succeed."""
    renamer = Renamer()
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
    ]
    for arc in arcs:
        arc.source.touch()
    renamer.perform_renamings(arcs)
    assert set(base.iterdir()) == set(arc.target for arc in arcs)
    assert renamer.get_log_contents() == "\n".join([
        "INFO:root:SOURCE:test/happy_path/source_0",
        "INFO:root:TARGET:test/happy_path/target_0",
        "INFO:root:SOURCE:test/happy_path/source_1",
        "INFO:root:TARGET:test/happy_path/target_1",
        "INFO:root:SOURCE:test/happy_path/source_2",
        "INFO:root:TARGET:test/happy_path/target_2",
    ])
    rm_tree(base)


def test_rename_and_undo():
    """All renamings succeed, then are successfully undone."""
    renamer = Renamer()
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
    ]
    for arc in arcs:
        arc.source.touch()
    renamer.perform_renamings(arcs)
    renamer.undo_renamings()
    assert set(base.iterdir()) == set(arc.source for arc in arcs)
    print(renamer.get_log_contents())
    assert renamer.get_log_contents() == "\n".join([
        "INFO:root:SOURCE:test/happy_path/target_2",
        "INFO:root:TARGET:test/happy_path/source_2",
        "INFO:root:SOURCE:test/happy_path/target_1",
        "INFO:root:TARGET:test/happy_path/source_1",
        "INFO:root:SOURCE:test/happy_path/target_0",
        "INFO:root:TARGET:test/happy_path/source_0",
    ])
    rm_tree(base)


def test_rename_and_undo_fail_after_target_deletion():
    """All renamings succeed, but undo them fails."""
    renamer = Renamer()
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
    ]
    for arc in arcs:
        arc.source.touch()
    renamer.perform_renamings(arcs)
    assert set(base.iterdir()) == set(arc.target for arc in arcs)
    arcs[1].target.unlink()  # delete a renamed file
    with pytest.raises(RecoverableRenamingError):
        renamer.undo_renamings()
    assert set(base.iterdir()) == {
        arcs[2].source, # correctly undone
        arcs[0].target, # failed to be undone
    }
    assert renamer.get_log_contents() == "\n".join([
        "INFO:root:SOURCE:test/happy_path/target_2",
        "INFO:root:TARGET:test/happy_path/source_2",
        "WARNING:root:[Errno 2] No such file or directory: 'test/happy_path/target_1' -> 'test/happy_path/source_1'",
    ])
    renamer.rollback_renamings()
    print(set(base.iterdir()))
    assert set(base.iterdir()) == {
        arcs[2].target, # correctly undone
        arcs[0].target, # failed to be undone
    }
    assert renamer.get_log_contents() == ""
    rm_tree(base)


def test_rename_and_undo_fail_after_log_file_deletion():
    """All renamings succeed, but undo them fails."""
    renamer = Renamer()
    base = Path("test") / "happy_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
    ]
    for arc in arcs:
        arc.source.touch()
    renamer.perform_renamings(arcs)
    assert set(base.iterdir()) == set(arc.target for arc in arcs)
    renamer.log_path.unlink()  # delete the log file
    with pytest.raises(Exception):
        renamer.undo_renamings()
    assert set(base.iterdir()) == set(arc.target for arc in arcs)
    rm_tree(base)


def test_rename_fail_and_rollback():
    """One renaming fails, but the previous ones are successfully rolled back."""
    renamer = Renamer()
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
        Arc(base / "source_3", base / "target_3"),
    ]
    for arc in arcs:
        arc.source.touch()
    arcs[2].source.unlink()  # delete a source
    with pytest.raises(RecoverableRenamingError):
        renamer.perform_renamings(arcs) # the renaming fails
    renamer.rollback_renamings() # but we can roll back the previous ones
    assert set(base.iterdir()) == {
        base / "source_0", # rolled back
        base / "source_1", # rolled back
        base / "source_3", # untouched
    }
    assert renamer.get_log_contents() == "" # the log file is empty
    rm_tree(base)


def test_rename_fail_and_rollback_and_undo():
    """Undoing a successful rollback is possible, but has no effect."""
    renamer = Renamer()
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
        Arc(base / "source_3", base / "target_3"),
    ]
    for arc in arcs:
        arc.source.touch()
    arcs[2].source.unlink()  # delete a source
    with pytest.raises(RecoverableRenamingError):
        renamer.perform_renamings(arcs) # the renaming fails
    renamer.rollback_renamings() # but we can roll back the previous ones
    renamer.undo_renamings()
    assert set(base.iterdir()) == {
        base / "source_0", # rolled back
        base / "source_1", # rolled back
        base / "source_3", # untouched
    }
    rm_tree(base)


def test_rename_fail_and_rollback_fail():
    """One renaming fails, and the previous ones fail to be rolled back."""
    renamer = Renamer()
    base = Path("test") / "rollback_path"
    rm_tree(base)
    base.mkdir()
    arcs = [
        Arc(base / "source_0", base / "target_0"),
        Arc(base / "source_1", base / "target_1"),
        Arc(base / "source_2", base / "target_2"),
        Arc(base / "source_3", base / "target_3"),
    ]
    for arc in arcs:
        arc.source.touch()
    arcs[2].source.unlink()  # delete a source
    with pytest.raises(RecoverableRenamingError):
        renamer.perform_renamings(arcs) # the renaming fails
    arcs[1].target.unlink() # delete a file already renamed
    with pytest.raises(FileNotFoundError):
       renamer.rollback_renamings() # the rollback fails
    print(renamer.get_log_contents())
    assert renamer.get_log_contents() == "\n".join([
        "INFO:root:SOURCE:test/rollback_path/source_0",
        "INFO:root:TARGET:test/rollback_path/target_0",
        "INFO:root:SOURCE:test/rollback_path/source_1",
        "INFO:root:TARGET:test/rollback_path/target_1",
        "WARNING:root:[Errno 2] No such file or directory: 'test/rollback_path/source_2' -> 'test/rollback_path/target_2'",
        "INFO:root:rollback",
        "ERROR:root:rollback:[Errno 2] No such file or directory: 'test/rollback_path/target_1' -> 'test/rollback_path/source_1'",
    ])
    with pytest.raises(Exception):
        renamer.undo_renamings() # The previous rollback failed. Undoing is not possible.
    rm_tree(base)


def test_undo_with_empty_log_file():
    renamer = Renamer()
    renamer.log_path.write_text("")
    renamer.undo_renamings() # doesn't raise an exception

if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
