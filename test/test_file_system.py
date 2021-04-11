import pytest

from pathlib import Path

import context
from src.file_system import FileSystem


def test_pure():
    paths = Path("test/fhs.txt").read_text().strip().split("\n")
    file_system = FileSystem(paths, is_pure=True)
    assert file_system.exists(Path("/usr/local"))
    assert file_system.index(Path("/usr/local")) == 48
    assert file_system.index(Path("/usr/local/a")) == 48
    file_system.add(Path("/usr/local/a"))
    assert file_system.index(Path("/usr/local/a")) == 49
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
    assert set(map(str, file_system.childs(Path("/usr")))) == set(expected + ["/usr/local"])
    assert result == expected
    file_system.add(Path("/usr/foo.bar"))
    new_path = file_system.uncollide(Path("/usr/foo.bar"))
    assert file_system.exists(Path("/usr/foo.bar"))
    assert file_system.exists(Path("/usr/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae-0.bar"))
    file_system.remove(Path("/usr/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae-0.bar"))
    assert not file_system.exists(Path("/usr/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae-0.bar"))
    file_system.rename(Path("/etc"), Path("/etcetera"))
    assert not file_system.exists(Path("/etc"))
    expected = [
        Path("/etcetera"),
        Path("/etcetera/X11"),
        Path("/etcetera/X11"),
        Path("/etcetera/opt"),
        Path("/etcetera/skel"),
        Path("/etcetera/skel"),
        Path("/etcetera/sysconfig"),
        Path("/etcetera/sysconfig"),
        Path("/etcetera/xinetd.d"),
    ]
    assert all(map(file_system.exists, expected))


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
