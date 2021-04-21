import pytest, subprocess
from pathlib import Path, PosixPath

import context
from src.file_renamer import *
from create_fhs import create_fhs


FILE_SYSTEM = FileSystem(Path("test/fhs.txt").read_text().strip().split("\n"), is_pure=True)


def test_parse_new_names():
    new_names_ok = [  # path -> new_name
        "#0# boom",  # /bin -> boom
        "#58# bam1",  # /usr/local/share/man/man1 -> bam1
        "#59# bam2",  # /usr/local/share/man/man2 -> bam2
        "#60# bam3",  # /usr/local/share/man/man3 -> bam3
        "#92# bar",  # /var -> bar
        "#105# optic",  # /var/opt -> optic
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
            Clause(Path("/usr/local/share/man/man1"), ""),
            Clause(Path("/usr/local/share/man/man4"), ""),
        ],
        [
            Clause(Path("/usr/share/man/man1"), ""),
            Clause(Path("/usr/share/man/man3"), ""),
            Clause(Path("/usr/share/man/man6"), ""),
        ],
        [
            Clause(Path("/etc/X11/applnk"), ""),
            Clause(Path("/etc/X11/starthere"), ""),
            Clause(Path("/usr/share/man"), ""),
            Clause(Path("/usr/share/misc"), ""),
            Clause(Path("/usr/lib/tls"), ""),
        ],
        [
            Clause(Path("/usr/tmp"), ""),
        ],
        [
            Clause(Path("/bin"), ""),
            Clause(Path("/var"), ""),
            Clause(Path("/sys"), ""),
        ],
    ]
    print(expected)

    assert sort_clauses(clauses) == expected


def test_create_edges():
    clauses1 = [
        Clause(Path("/usr/share/man/man1"), "spam"),
        Clause(Path("/usr/share/man/man2"), "eggs"),
        Clause(Path("/usr/share/man/man3"), "sausage"),
    ]

    expected1 = Edges(
        [],
        [
            Edge(Path("/usr/share/man/man3"), Path("/usr/share/man/sausage")),
            Edge(Path("/usr/share/man/man2"), Path("/usr/share/man/eggs")),
            Edge(Path("/usr/share/man/man1"), Path("/usr/share/man/spam")),
        ],
    )

    clauses2 = [
        Clause(Path("/usr/share/"), "spam"),
        Clause(Path("/usr/share/man"), "eggs"),
        Clause(Path("/usr/share/man/mann"), "sausage"),
    ]

    expected2 = Edges(
        [],
        [
            Edge(Path("/usr/share/man/mann"), Path("/usr/share/man/sausage")),
            Edge(Path("/usr/share/man"), Path("/usr/share/eggs")),
            Edge(Path("/usr/share/"), Path("/usr/spam")),
        ],
    )

    clauses3 = [
        Clause(Path("/usr/share/man/man1"), "man3"),
        Clause(Path("/usr/share/man/man2"), "man1"),
        Clause(Path("/usr/share/man/man3"), "man2"),
    ]

    clauses3_hashes = [
        FILE_SYSTEM.uncollide(clauses3[0].path),
        FILE_SYSTEM.uncollide(clauses3[1].path),
        FILE_SYSTEM.uncollide(clauses3[2].path),
    ]

    for h in clauses3_hashes:
        FILE_SYSTEM.as_set.remove(h)

    expected3 = Edges(
        [
            Edge(Path("/usr/share/man/man1"), clauses3_hashes[0]),
            Edge(Path("/usr/share/man/man2"), clauses3_hashes[1]),
            Edge(Path("/usr/share/man/man3"), clauses3_hashes[2]),
        ],
        [
            Edge(clauses3_hashes[0], Path("/usr/share/man/man3")),
            Edge(clauses3_hashes[1], Path("/usr/share/man/man1")),
            Edge(clauses3_hashes[2], Path("/usr/share/man/man2")),
        ],
    )

    assert create_edges(clauses1, FILE_SYSTEM) == expected1
    assert create_edges(clauses2, FILE_SYSTEM) == expected2
    assert create_edges(clauses3, FILE_SYSTEM) == expected3


def test_renamer_pure():
    new_names = [  # path -> new_name
        "#1# reboot",  # /boot -> reboot
        "#2# etcetera",  # /etc -> etcetera
        "#96# library",  # /var/lib -> library
        "#76# superman",  # /usr/share/man -> superman
        "#77# man3",  # /usr/share/man/man1 -> man3
        "#78# man1",  # /usr/share/man/man2 -> man1
        "#79# man2",  # /usr/share/man/man3 -> man2
        "#80# man5",  # /usr/share/man/man4 -> man5
        "#81# man55",  # /usr/share/man/man5 -> man55
        "#103# miel",  # /var/mail -> miel
    ]

    expected = [
        Path("/reboot"),
        Path("/etcetera"),
        Path("/etcetera/X11"),
        Path("/etcetera/opt"),
        Path("/etcetera/skel"),
        Path("/etcetera/sysconfig"),
        Path("/etcetera/xinetd.d"),
        Path("/var/library"),
        Path("/var/library/games"),
        Path("/var/library/misc"),
        Path("/usr/share/superman"),
        Path("/usr/share/superman/man1"),
        Path("/usr/share/superman/man2"),
        Path("/usr/share/superman/man3"),
        Path("/usr/share/superman/man5"),
        Path("/usr/share/superman/man55"),
        Path("/usr/share/superman/man6"),
        Path("/usr/share/superman/man7"),
        Path("/usr/share/superman/man8"),
        Path("/usr/share/superman/man9"),
        Path("/usr/share/superman/mann"),
        Path("/var/miel"),
    ]

    not_expected = [
        Path("/boot"),
        Path("/etc"),
        Path("/etc/X11"),
        Path("/etc/opt"),
        Path("/etc/skel"),
        Path("/etc/sysconfig"),
        Path("/etc/xinetd.d"),
        Path("/var/lib"),
        Path("/var/lib/games"),
        Path("/var/lib/misc"),
        Path("/var/mail"),
        Path("/usr/share/man"),
        Path("/usr/share/man/man1"),
        Path("/usr/share/man/man2"),
        Path("/usr/share/man/man3"),
        Path("/usr/share/man/man4"),
        Path("/usr/share/man/man5"),
        Path("/usr/share/man/man6"),
        Path("/usr/share/man/man7"),
        Path("/usr/share/man/man8"),
        Path("/usr/share/man/man9"),
        Path("/usr/share/man/mann"),
        Path("/usr/share/superman/man4"),
    ]

    clauses = sort_clauses(parse_new_names(FILE_SYSTEM, new_names))
    renamer(clauses, FILE_SYSTEM)

    assert all(map(FILE_SYSTEM.exists, expected))
    assert not all(map(FILE_SYSTEM.exists, not_expected))


def test_renamer_system():
    create_fhs()
    file_system = FileSystem(
        [
            Path("test/FHS/etc"),
            Path("test/FHS/lib"),
            Path("test/FHS/etc/X11"),
            Path("test/FHS/var/lib"),
            Path("test/FHS/var/log"),
            Path("test/FHS/var/mail"),
            Path("test/FHS/usr/share/man"),
            Path("test/FHS/usr/share/man/man1"),
            Path("test/FHS/usr/share/man/man2"),
            Path("test/FHS/usr/share/man/man3"),
            Path("test/FHS/usr/share/man/man4"),
            Path("test/FHS/usr/share/man/man5"),
            Path("test/FHS/usr/share/man/man6"),
        ]
    )

    new_names = [
        f"#{Path('test/FHS/etc').stat().st_ino}# etcetera",
        f"#{Path('test/FHS/lib').stat().st_ino}# library",
        f"#{Path('test/FHS/etc/X11').stat().st_ino}# X",
        f"#{Path('test/FHS/var/lib').stat().st_ino}# log",
        f"#{Path('test/FHS/var/log').stat().st_ino}# lib",
        f"#{Path('test/FHS/var/mail').stat().st_ino}# spam",
        f"#{Path('test/FHS/usr/share/man').stat().st_ino}# superman",
        f"#{Path('test/FHS/usr/share/man/man1').stat().st_ino}# man3",
        f"#{Path('test/FHS/usr/share/man/man2').stat().st_ino}# man1",
        f"#{Path('test/FHS/usr/share/man/man3').stat().st_ino}# man2",
        f"#{Path('test/FHS/usr/share/man/man4').stat().st_ino}# man4",
        f"#{Path('test/FHS/usr/share/man/man5').stat().st_ino}# man6",
        f"#{Path('test/FHS/usr/share/man/man6').stat().st_ino}# man66",
    ]

    clauses = sort_clauses(parse_new_names(file_system, new_names))
    renamer(clauses, file_system)

    expected = [
        Path("test/FHS/etcetera"),
        Path("test/FHS/library"),
        Path("test/FHS/etcetera/X"),
        Path("test/FHS/etcetera/X/applnk"),
        Path("test/FHS/etcetera/X/serverconfig"),
        Path("test/FHS/etcetera/X/starthere"),
        Path("test/FHS/etcetera/X/sysconfig"),
        Path("test/FHS/var/lib"),
        Path("test/FHS/var/log"),
        Path("test/FHS/var/log/games"),
        Path("test/FHS/var/log/misc"),
        Path("test/FHS/var/spam"),
        Path("test/FHS/usr/share/superman"),
        Path("test/FHS/usr/share/superman/man1"),
        Path("test/FHS/usr/share/superman/man2"),
        Path("test/FHS/usr/share/superman/man3"),
        Path("test/FHS/usr/share/superman/man4"),
        Path("test/FHS/usr/share/superman/man6"),
        Path("test/FHS/usr/share/superman/man66"),
    ]

    not_expected = [
        Path("test/FHS/etc"),
        Path("test/FHS/lib"),
        Path("test/FHS/etc/X11"),
        Path("test/FHS/etc/X11/applnk"),
        Path("test/FHS/etc/X11/serverconfig"),
        Path("test/FHS/etc/X11/starthere"),
        Path("test/FHS/etc/X11/sysconfig"),
        Path("test/FHS/var/lib/games"),
        Path("test/FHS/var/lib/misc"),
        Path("test/FHS/var/mail"),
        Path("test/FHS/usr/share/man"),
        Path("test/FHS/usr/share/man/man1"),
        Path("test/FHS/usr/share/man/man2"),
        Path("test/FHS/usr/share/man/man3"),
        Path("test/FHS/usr/share/man/man4"),
        Path("test/FHS/usr/share/superman/man5"),
    ]

    assert all(x.exists() for x in expected)
    assert not all(x.exists() for x in not_expected)

    subprocess.run(["rm", "-rf", "test/FHS"])


def test_unrenamer():
    create_fhs()
    file_system = FileSystem(
        [
            Path("test/FHS/etc"),
            Path("test/FHS/lib"),
            Path("test/FHS/etc/X11"),
            Path("test/FHS/var/lib"),
            Path("test/FHS/var/log"),
            Path("test/FHS/var/mail"),
            Path("test/FHS/usr/share/man"),
            Path("test/FHS/usr/share/man/man1"),
            Path("test/FHS/usr/share/man/man2"),
            Path("test/FHS/usr/share/man/man3"),
            Path("test/FHS/usr/share/man/man4"),
            Path("test/FHS/usr/share/man/man5"),
            Path("test/FHS/usr/share/man/man6"),
        ]
    )

    new_names = [
        f"#{Path('test/FHS/etc').stat().st_ino}# etcetera",
        f"#{Path('test/FHS/lib').stat().st_ino}# library",
        f"#{Path('test/FHS/etc/X11').stat().st_ino}# X",
        f"#{Path('test/FHS/var/lib').stat().st_ino}# log",
        f"#{Path('test/FHS/var/log').stat().st_ino}# lib",
        f"#{Path('test/FHS/var/mail').stat().st_ino}# spam",
        f"#{Path('test/FHS/usr/share/man').stat().st_ino}# superman",
        f"#{Path('test/FHS/usr/share/man/man1').stat().st_ino}# man3",
        f"#{Path('test/FHS/usr/share/man/man2').stat().st_ino}# man1",
        f"#{Path('test/FHS/usr/share/man/man3').stat().st_ino}# man2",
        f"#{Path('test/FHS/usr/share/man/man4').stat().st_ino}# man4",
        f"#{Path('test/FHS/usr/share/man/man5').stat().st_ino}# man6",
        f"#{Path('test/FHS/usr/share/man/man6').stat().st_ino}# man66",
    ]

    clauses = sort_clauses(parse_new_names(file_system, new_names))
    completed_renames = []
    renamer(clauses, file_system, completed_renames)
    unrenamer(file_system, completed_renames)

    expected = [
        Path("test/FHS/etc"),
        Path("test/FHS/lib"),
        Path("test/FHS/etc/X11"),
        Path("test/FHS/etc/X11/applnk"),
        Path("test/FHS/etc/X11/serverconfig"),
        Path("test/FHS/etc/X11/starthere"),
        Path("test/FHS/etc/X11/sysconfig"),
        Path("test/FHS/var/lib/games"),
        Path("test/FHS/var/lib/misc"),
        Path("test/FHS/var/mail"),
        Path("test/FHS/usr/share/man"),
        Path("test/FHS/usr/share/man/man1"),
        Path("test/FHS/usr/share/man/man2"),
        Path("test/FHS/usr/share/man/man3"),
        Path("test/FHS/usr/share/man/man4"),
        Path("test/FHS/usr/share/man/man5"),
        Path("test/FHS/var/lib/games"),
        Path("test/FHS/var/lib/misc"),
    ]

    not_expected = [
        Path("test/FHS/etcetera"),
        Path("test/FHS/library"),
        Path("test/FHS/etcetera/X"),
        Path("test/FHS/etcetera/X/applnk"),
        Path("test/FHS/etcetera/X/serverconfig"),
        Path("test/FHS/etcetera/X/starthere"),
        Path("test/FHS/etcetera/X/sysconfig"),
        Path("test/FHS/var/log/games"),
        Path("test/FHS/var/log/misc"),
        Path("test/FHS/var/spam"),
        Path("test/FHS/usr/share/superman"),
        Path("test/FHS/usr/share/superman/man1"),
        Path("test/FHS/usr/share/superman/man2"),
        Path("test/FHS/usr/share/superman/man3"),
        Path("test/FHS/usr/share/superman/man4"),
        Path("test/FHS/usr/share/superman/man6"),
        Path("test/FHS/usr/share/superman/man66"),
    ]

    assert all(x.exists() for x in expected)
    assert not all(x.exists() for x in not_expected)

    subprocess.run(["rm", "-rf", "test/FHS"])


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
