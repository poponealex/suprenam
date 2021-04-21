import pytest

from pathlib import Path

import context
from src.renamer import check_and_complete, sorted_by_level


@pytest.fixture(scope="module")
def base_path():
    return Path(".").resolve()


@pytest.fixture()
def paths(base_path):
    return [
        base_path / "src" / "goodies.py",
        base_path / "src" / "goodies.py",  # duplicates don't matter
        base_path / "test" / "context.py",
    ]


def test_check_and_complete(base_path, paths):
    result = check_and_complete(paths)
    assert Path(base_path / "src" / "goodies.py") in result
    assert Path(base_path / "test" / "context.py") in result
    assert Path(base_path / "src" / "file_system.py") in result
    assert Path(base_path / "src") not in result


def test_check_and_complete_failed(base_path, paths):
    paths.append(Path(base_path / "non_existing_node"))
    with pytest.raises(FileNotFoundError):
        check_and_complete(paths)


def test_sorted_by_level():
    _ = "whatever"
    clauses = {
        Path("/sys"): _,
        Path("/tmp"): _,
        Path("/usr"): _,
        Path("/usr/X11R6"): _,
        Path("/usr/X11R6/bin"): _,
        Path("/usr/X11R6/include"): _,
        Path("/usr/X11R6/lib"): _,
        Path("/usr/X11R6/lib/tls"): _,
        Path("/usr/X11R6/man"): _,
        Path("/usr/X11R6/share"): _,
        Path("/usr/bin"): _,
        Path("/usr/bin/X11"): _,
    }
    expected = [
        (Path("/sys"), _),
        (Path("/tmp"), _),
        (Path("/usr"), _),
        (Path("/usr/X11R6"), _),
        (Path("/usr/bin"), _),
        (Path("/usr/X11R6/bin"), _),
        (Path("/usr/X11R6/include"), _),
        (Path("/usr/X11R6/lib"), _),
        (Path("/usr/X11R6/man"), _),
        (Path("/usr/X11R6/share"), _),
        (Path("/usr/bin/X11"), _),
        (Path("/usr/X11R6/lib/tls"), _),
    ]
    result = sorted_by_level(clauses)
    assert list(result) == expected


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
