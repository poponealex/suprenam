import pytest

from pathlib import Path

import context
from src.file_system import FileSystem
from pathvalidate import ValidationError


@pytest.fixture(scope="module")
def paths():
    return [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]


@pytest.fixture()
def fs(paths):
    return FileSystem(paths)


def test_constructor(fs):
    assert Path("/usr/local") in fs


path_and_platform_data = [
    ([Path("/foo/bar\0")], "linux"),
    ([Path("/foo/bar\0")], "macOS"),
    ([Path("/foo/bar?")], "Windows"),
]

@pytest.mark.parametrize("paths, platform", path_and_platform_data)
def test_invalid_pure_filenames(paths, platform):
    with pytest.raises(ValidationError):
        FileSystem(paths, platform)


def test_update_with_source_paths_concrete():
    fs = FileSystem()
    paths = [
        Path("./src/goodies.py"),
        Path("."),
    ]
    fs.update_with_source_paths(paths)
    assert Path("./src/file_system.py") in fs  # sibling of `goodies.py`
    assert Path("./test") in fs  # sibling of `.`
    assert Path("./LICENSE") in fs  # sibling of `.`
    assert Path("./test/test_file_system.py") not in fs  # child of a sibling of `.`


def test_update_with_source_paths_not_existing(fs):
    paths = [
        Path("/foo/bar"),
    ]
    with pytest.raises(FileNotFoundError) as offending_path:
        fs.update_with_source_paths(paths)
    assert offending_path.value.args[0] == Path("/foo/bar")


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
        Path("/usr/X11R6"),
        Path("/usr/bin"),
        Path("/usr/etc"),
        Path("/usr/games"),
        Path("/usr/include"),
        Path("/usr/lib"),
        Path("/usr/libexec"),
        Path("/usr/local"),  # a node is considered as its own sibling
        Path("/usr/sbin"),
        Path("/usr/share"),
        Path("/usr/src"),
        Path("/usr/tmp"),
    }
    result = set(fs.siblings(Path("/usr/local")))
    assert result == expected


def test_non_existing_sibling_folder(fs):
    expected = "/usr/NRXWGYLM-0"
    result = str(fs.non_existing_sibling(Path("/usr/local")))
    assert result == expected


def test_non_existing_sibling_file(fs):
    expected = "/etc/PBUW4ZLUMQXGI===-0"
    result = str(fs.non_existing_sibling(Path("/etc/xinetd.d")))
    assert result == expected


def test_non_existing_sibling_file_with_collision(fs):
    fs.add(Path("/etc/PBUW4ZLUMQXGI===-0"))
    expected = "/etc/PBUW4ZLUMQXGI===-1"
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


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
