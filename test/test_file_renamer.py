from pathlib import Path, PosixPath
import context
from src.file_renamer import *
import pytest


FILE_SYSTEM = FileSystem(Path("test/fhs.txt").read_text().strip().split("\n"), is_pure=True)


def test_parse_new_names():
    new_names_ok = [
        "#0# boom",
        "#58# bam1",
        "#59# bam2",
        "#60# bam3",
        "#92# bar",
        "#105# optic",
    ]

    expected = [
        Clause(FILE_SYSTEM.as_population["0"], "boom"),
        Clause(FILE_SYSTEM.as_population["58"], "bam1"),
        Clause(FILE_SYSTEM.as_population["59"], "bam2"),
        Clause(FILE_SYSTEM.as_population["60"], "bam3"),
        Clause(FILE_SYSTEM.as_population["92"], "bar"),
        Clause(FILE_SYSTEM.as_population["105"], "optic"),
    ]

    fail_illegal_char = [
        "#0# boo/m",
        "#58# bam1",
        "#59# bam2",
        "#60# ba/m3",
        "#92# bar",
        "#105# optic",
    ]

    fail_existing_filename = [
        "#0# boom",
        "#58# man2",
        "#59# ban3",
        "#60# man4",  # man4 already exists
        "#92# bar",
        "#105# optic",
    ]

    fail_giving_two_siblings_the_same_name = [
        "#0# boom",
        "#58# bam",
        "#59# bam",
        "#60# bam3",
        "#92# bar",
        "#105# optic",
    ]

    assert parse_new_names(FILE_SYSTEM, new_names_ok) == expected

    with pytest.raises(ValueError):
        parse_new_names(FILE_SYSTEM, fail_illegal_char)
        parse_new_names(FILE_SYSTEM, fail_existing_filename)
        parse_new_names(FILE_SYSTEM, fail_giving_two_siblings_the_same_name)


def test_sort_clauses():
    clauses = [
        Clause(Path("/bin"), ""),
        Clause(Path("/etc/X11/applnk"), ""),
        Clause(Path("/etc/X11/starthere"), ""),
        Clause(Path("/usr/share/man/man1"), ""),
        Clause(Path("/usr/share/man"), ""),
        Clause(Path("/usr/local/share/man/man1"), ""),
        Clause(Path("/var"), ""),
        Clause(Path("/usr/share/misc"), ""),
        Clause(Path("/usr/share/man/man3"), ""),
        Clause(Path("/usr/local/share/man/man4"), ""),
        Clause(Path("/usr/lib/tls"), ""),
        Clause(Path("/usr/share/man/man6"), ""),
        Clause(Path("/usr/tmp"), ""),
        Clause(Path("/sys"), ""),
    ]

    expected = [
        [
            Clause(Path("/usr/local/share/man/man4"), ""),
            Clause(Path("/usr/local/share/man/man1"), ""),
        ],
        [
            Clause(Path("/usr/share/man/man6"), ""),
            Clause(Path("/usr/share/man/man3"), ""),
            Clause(Path("/usr/share/man/man1"), ""),
        ],
        [
            Clause(Path("/usr/lib/tls"), ""),
            Clause(Path("/usr/share/misc"), ""),
            Clause(Path("/usr/share/man"), ""),
            Clause(Path("/etc/X11/starthere"), ""),
            Clause(Path("/etc/X11/applnk"), ""),
        ],
        [
            Clause(Path("/usr/tmp"), ""),
        ],
        [
            Clause(Path("/sys"), ""),
            Clause(Path("/var"), ""),
            Clause(Path("/bin"), ""),
        ],
    ]

    assert sort_clauses(clauses) == expected


def test_create_edges():
    clauses1 = [
        Clause(Path("/usr/share/man/man1"), "spam"),
        Clause(Path("/usr/share/man/man2"), "eggs"),
        Clause(Path("/usr/share/man/man3"), "sausage"),
    ]

    clauses1_hashes = [
        FILE_SYSTEM.uncollide(clauses1[0].path),
        FILE_SYSTEM.uncollide(clauses1[1].path),
        FILE_SYSTEM.uncollide(clauses1[2].path),
    ]

    for h in clauses1_hashes:
        FILE_SYSTEM.as_set.remove(h)

    expected1 = Edges(
        [
            Edge(Path("/usr/share/man/man1"), clauses1_hashes[0]),
            Edge(Path("/usr/share/man/man2"), clauses1_hashes[1]),
            Edge(Path("/usr/share/man/man3"), clauses1_hashes[2]),
        ],
        [
            Edge(clauses1_hashes[0], Path("/usr/share/man/spam")),
            Edge(clauses1_hashes[1], Path("/usr/share/man/eggs")),
            Edge(clauses1_hashes[2], Path("/usr/share/man/sausage")),
        ],
    )

    clauses2 = [
        Clause(Path("/usr/share/"), "spam"),
        Clause(Path("/usr/share/man"), "eggs"),
        Clause(Path("/usr/share/man/mann"), "sausage"),
    ]

    clauses2_hashes = [
        FILE_SYSTEM.uncollide(clauses2[0].path),
        FILE_SYSTEM.uncollide(clauses2[1].path),
        FILE_SYSTEM.uncollide(clauses2[2].path),
    ]

    for h in clauses2_hashes:
        FILE_SYSTEM.as_set.remove(h)

    expected2 = Edges(
        [
            Edge(Path("/usr/share/"), clauses2_hashes[0]),
            Edge(Path("/usr/share/man"), clauses2_hashes[1]),
            Edge(Path("/usr/share/man/mann"), clauses2_hashes[2]),
        ],
        [
            Edge(clauses2_hashes[0], Path("/usr/spam")),
            Edge(clauses2_hashes[1], Path("/usr/share/eggs")),
            Edge(clauses2_hashes[2], Path("/usr/share/man/sausage")),
        ],
    )

    assert create_edges(clauses1, FILE_SYSTEM) == expected1
    assert create_edges(clauses2, FILE_SYSTEM) == expected2


def test_renamer():
    new_names = [
        "#1# reboot",
        "#2# etcetera",
        "#96# library",
        "#76# superman",
        "#77# man3",
        "#78# man1",
        "#79# man2",
        "#103# miel",
    ]

    clauses = sort_clauses(parse_new_names(FILE_SYSTEM, new_names))
    renamer(clauses, FILE_SYSTEM, is_pure=True)

    assert not FILE_SYSTEM.exists(Path("/boot"))
    assert FILE_SYSTEM.exists(Path("/reboot"))
    assert not FILE_SYSTEM.exists(Path("/etc"))
    assert FILE_SYSTEM.exists(Path("/etcetera"))
    assert FILE_SYSTEM.exists(Path("/etcetera/X11"))
    assert FILE_SYSTEM.exists(Path("/etcetera/opt"))
    assert FILE_SYSTEM.exists(Path("/etcetera/skel"))
    assert FILE_SYSTEM.exists(Path("/etcetera/sysconfig"))
    assert FILE_SYSTEM.exists(Path("/etcetera/xinetd.d"))
    assert not FILE_SYSTEM.exists(Path("/var/lib"))
    assert FILE_SYSTEM.exists(Path("/var/library"))
    assert FILE_SYSTEM.exists(Path("/var/library/games"))
    assert FILE_SYSTEM.exists(Path("/var/library/misc"))
    assert not FILE_SYSTEM.exists(Path("/usr/share/man"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man1"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man2"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man3"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man4"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man5"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man6"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man7"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man8"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/man9"))
    assert FILE_SYSTEM.exists(Path("/usr/share/superman/mann"))
    assert not FILE_SYSTEM.exists(Path("/var/mail"))
    assert FILE_SYSTEM.exists(Path("/var/miel"))


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
