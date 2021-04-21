import pytest

from pathlib import Path

import context
from src.file_system import PureFileSystem


@pytest.fixture(scope="module")
def paths():
    return Path("test/fhs.txt").read_text().strip().split("\n")


@pytest.fixture()
def pfs(paths):
    return PureFileSystem(paths)


def test_constructor(pfs):
    assert Path("/usr/local") in pfs


def test_children(pfs):
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
    result = set(map(str, pfs.children(Path("/usr"))))
    assert result == expected


def test_siblings(pfs):
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
    result = set(map(str, pfs.siblings(Path("/usr/local"))))
    assert result == expected


def test_non_existing_sibling_folder(pfs):
    expected = "/usr/25bf8e1a2393f1108d37029b3df55932-0"
    result = str(pfs.non_existing_sibling(Path("/usr/local")))
    assert result == expected


def test_non_existing_sibling_file(pfs):
    expected = "/etc/6184c2e07c47afbd767e35fe6e07b824-0.d"
    result = str(pfs.non_existing_sibling(Path("/etc/xinetd.d")))
    assert result == expected


def test_non_existing_sibling_file_with_collision(pfs):
    pfs.add(Path("/etc/6184c2e07c47afbd767e35fe6e07b824-0.d"))
    expected = "/etc/6184c2e07c47afbd767e35fe6e07b824-1.d"
    result = str(pfs.non_existing_sibling(Path("/etc/xinetd.d")))
    assert result == expected


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
