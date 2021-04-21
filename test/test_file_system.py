import pytest

from pathlib import Path

import context
from src.file_system import FileSystem


@pytest.fixture(scope="module")
def paths():
    return [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]


@pytest.fixture()
def fs(paths):
    return FileSystem(paths)


def test_constructor(fs):
    assert Path("/usr/local") in fs


def test_children(fs):
    expected = {
        "/usr/X11R6",
        "/usr/bin",
        "/usr/etc",
        "/usr/games",
        "/usr/include",
        "/usr/lib",
        "/usr/libexec",
        "/usr/local",
        "/usr/sbin",
        "/usr/share",
        "/usr/src",
        "/usr/tmp",
    }
    result = set(map(str, fs.children(Path("/usr"))))
    assert result == expected


def test_siblings(fs):
    expected = {
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
    }
    result = set(map(str, fs.siblings(Path("/usr/local"))))
    assert result == expected


def test_non_existing_sibling_folder(fs):
    expected = "/usr/25bf8e1a2393f1108d37029b3df55932-0"
    result = str(fs.non_existing_sibling(Path("/usr/local")))
    assert result == expected


def test_non_existing_sibling_file(fs):
    expected = "/etc/6184c2e07c47afbd767e35fe6e07b824-0.d"
    result = str(fs.non_existing_sibling(Path("/etc/xinetd.d")))
    assert result == expected


def test_non_existing_sibling_file_with_collision(fs):
    fs.add(Path("/etc/6184c2e07c47afbd767e35fe6e07b824-0.d"))
    expected = "/etc/6184c2e07c47afbd767e35fe6e07b824-1.d"
    result = str(fs.non_existing_sibling(Path("/etc/xinetd.d")))
    assert result == expected


def test_rename_leaf(fs):
    original_fs = set(fs)
    fs.rename(Path("/mnt/floppy"), Path("/mnt/toaster"))
    assert original_fs - fs == {Path("/mnt/floppy")}
    assert fs - original_fs == {Path("/mnt/toaster")}


def test_rename_internal_node(fs):
    original_fs = set(fs)
    fs.rename(Path("/usr/X11R6"), Path("/usr/foobar"))
    assert original_fs - fs == {
        Path("/usr/X11R6"),
        Path("/usr/X11R6/bin"),
        Path("/usr/X11R6/include"),
        Path("/usr/X11R6/lib"),
        Path("/usr/X11R6/lib/tls"),
        Path("/usr/X11R6/man"),
        Path("/usr/X11R6/share"),
    }
    assert fs - original_fs == {
        Path("/usr/foobar"),
        Path("/usr/foobar/bin"),
        Path("/usr/foobar/include"),
        Path("/usr/foobar/lib"),
        Path("/usr/foobar/lib/tls"),
        Path("/usr/foobar/man"),
        Path("/usr/foobar/share"),
    }


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
