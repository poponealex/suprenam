import pytest

from pathlib import Path

import context
from src.file_system import FileSystem


def test_pure():
    paths = Path("test/fhs.txt").read_text().strip().split("\n")
    file_system = FileSystem(paths, is_pure=True)
    assert file_system.exists(Path("/usr/local"))
    assert not file_system.exists(Path("/usr/non_existing_node"))
    result = list(map(str, file_system.siblings(Path("/usr/local"))))
    expected = [
        "/usr/X11R6",
        "/usr/bin",
        "/usr/etc",
        "/usr/games",
        "/usr/include",
        "/usr/lib",
        "/usr/libexec",
        "/usr/sbin",
        "/usr/share",
        "/usr/src",
        "/usr/tmp",
    ]
    assert result == expected


def test_actual():
    base_path = Path(".").resolve()
    paths = [
        base_path / "src" / "goodies.py",
        base_path / "test" / "context.py",
        base_path / "non_existing_node",
    ]
    with pytest.raises(FileNotFoundError):
        file_system = FileSystem(paths)
    paths.pop()  # suppress the offending non existing path
    file_system = FileSystem(paths)
    assert file_system.exists(Path(base_path / "src" / "file_system.py"))
    assert not file_system.exists(Path(base_path / "src"))
    path = Path(base_path / "test" / "fhs.txt")
    result = list(file_system.siblings(path))
    assert path not in result, "A path is not its own sibling."
    assert Path(base_path / "test" / "examples.md") in result
    assert Path(base_path / "src" / "goodies.py") not in result


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
