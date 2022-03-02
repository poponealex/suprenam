import pytest

from pathlib import Path

import context
from src.secure_clauses import *


@pytest.fixture(scope="module")
def paths():
    return [Path(line) for line in Path("test/fhs.txt").read_text().strip().split("\n")]


@pytest.fixture()
def fs(paths):
    return FileSystem(paths)


def test_secure_clauses(fs):
    clauses = [
        (Path("/usr/X11R6/include"), "foobar"),
        (Path("/usr/local"), "bocal"),
        (Path("/usr/include"), "lib"),
        (Path("/usr/lib"), "include"),
    ]
    result = secure_clauses(fs, clauses)
    assert result == [
        (Path("/usr/X11R6/include"), Path("/usr/X11R6/foobar")),
        (Path("/usr/local"), Path("/usr/bocal")),
        (Path("/usr/include"), Path("/usr/NFXGG3DVMRSQ====-0")),
        (Path("/usr/lib"), Path("/usr/include")),
        (Path("/usr/NFXGG3DVMRSQ====-0"), Path("/usr/lib")),
    ]
    expected_fs_subset = {
        Path("/usr/bin"),
        Path("/usr/X11R6"),
        Path("/usr/libexec"),
        Path("/usr/X11R6/share"),
        Path("/usr/X11R6/foobar"),  # new path
        Path("/usr/src"),
        Path("/usr/X11R6/lib"),
        Path("/usr/bocal/share/man/man4"),  # new path
        Path("/usr/bocal/share/info"),  # new path
        Path("/usr/bocal/share/man/man2"),  # new path
        Path("/usr/bocal/src"),  # new path
        Path("/usr/bocal/libexec"),  # new path
        Path("/usr/bocal/share/man/man3"),  # new path
        Path("/usr/bocal/etc"),  # new path
        Path("/usr/bocal/bin"),  # new path
        Path("/usr/bocal/lib"),  # new path
        Path("/usr/bocal/include"),  # new path
        Path("/usr/bocal/share/man/man8"),  # new path
        Path("/usr/bocal"),  # new path
        Path("/usr/bocal/games"),  # new path
        Path("/usr/bocal/sbin"),  # new path
        Path("/usr/bocal/share/man/man6"),  # new path
        Path("/usr/bocal/share/man/man5"),  # new path
        Path("/usr/bocal/share/man"),  # new path
        Path("/usr/bocal/share/man/man1"),  # new path
        Path("/usr/bocal/share/man/man9"),  # new path
        Path("/usr/bocal/share/man/man7"),  # new path
        Path("/usr/bocal/share"),  # new path
        Path("/usr/bocal/share/man/mann"),  # new path
        Path("/usr/share"),
        Path("/usr/tmp"),
        Path("/usr/X11R6/man"),
        Path("/usr/include"),  # swapped path
        Path("/usr/lib"),  # swapped path
        Path("/usr/etc"),
        Path("/usr/sbin"),
        Path("/usr/games"),
        Path("/usr/X11R6/bin"),
    }
    assert expected_fs_subset.issubset(fs)


def test_secure_clauses_with_intermediate_clash(fs):
    clauses = [
        (Path("/usr/X11R6/lib"), "man"),
        (Path("/usr/X11R6/man"), "foo"),
        (Path("/usr/X11R6"), "bar"),
    ]
    result = secure_clauses(fs, clauses)
    assert result == [
        (Path("/usr/X11R6/lib"), Path("/usr/X11R6/NRUWE===-0")),
        (Path("/usr/X11R6/man"), Path("/usr/X11R6/foo")),
        (Path("/usr/X11R6/NRUWE===-0"), Path("/usr/X11R6/man")),
        (Path("/usr/X11R6"), Path("/usr/bar")),
    ]


def test_dict_of_clauses():
    clauses = [
        (Path("/foo/bar"), "buzz"),
        (Path("/ping"), "pong"),
        (Path("/ping"), "pong"),  # duplicates are forbidden
    ]
    with pytest.raises(DuplicatedClauseError) as offending_path:
        dict_of_clauses(clauses)
    assert offending_path.value.args[0] == "The clause '/ping' -> 'pong' is given twice."


def test_dict_of_clauses_when_not_a_function():
    clauses = [
        (Path("/foo/bar"), "buzz"),
        (Path("/ping"), "pong"),
        (Path("/ping"), "fail"),  # contradiction
    ]
    with pytest.raises(SeveralTargetsError) as offending_path:
        dict_of_clauses(clauses)
    assert offending_path.value.args[0] == "Two distinct renaming targets for '/ping': 'pong' and 'fail'."


def test_check_injectivity(fs):
    clauses = {
        Path("/usr/X11R6"): "R2D2",
        Path("/usr"): "User System Resources",
        Path("/usr/bin/X11"): "R2D2",
        Path("/usr/lib/X11"): "R2D2",
    }
    assert check_injectivity(fs, clauses) is None


def test_check_injectivity_with_internal_problem(fs):
    clauses = {
        Path("/usr/lib/games"): "foobar",
        Path("/usr/lib/X11"): "foobar",
    }
    with pytest.raises(SeveralSourcesError) as offending_path:
        check_injectivity(fs, clauses)
    assert offending_path.value.args[0] == "At least two distinct sources for '/usr/lib/foobar'."


def test_check_injectivity_with_external_problem(fs):
    clauses = {
        Path("/usr/lib/games"): "X11",
    }
    with pytest.raises(SeveralSourcesError) as offending_path:
        check_injectivity(fs, clauses)
    assert offending_path.value.args[0] == "At least two distinct sources for '/usr/lib/X11'."


def test_sorted_by_level():
    _ = "whatever"
    clause_dict = {
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
        (
            5,
            [
                (Path("/usr/X11R6/lib/tls"), _),
            ],
        ),
        (
            4,
            [
                (Path("/usr/X11R6/bin"), _),
                (Path("/usr/X11R6/include"), _),
                (Path("/usr/X11R6/lib"), _),
                (Path("/usr/X11R6/man"), _),
                (Path("/usr/X11R6/share"), _),
                (Path("/usr/bin/X11"), _),
            ],
        ),
        (
            3,
            [
                (Path("/usr/X11R6"), _),
                (Path("/usr/bin"), _),
            ],
        ),
        (
            2,
            [
                (Path("/sys"), _),
                (Path("/tmp"), _),
                (Path("/usr"), _),
            ],
        ),
    ]
    result = sorted_by_level(clause_dict)
    assert result == expected


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
