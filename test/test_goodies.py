import pytest

__import__("sys").path[0:0] = "."
from src.goodies import *

remove_diacritics_data = [
    ("hello, world", "hello, world"),
    ("42", "42"),
    ("你好，世界", "你好，世界"),
    (
        "Dès Noël, où un zéphyr haï me vêt de glaçons würmiens, je dîne d’exquis rôtis de bœuf au kir, à l’aÿ d’âge mûr, &cætera.",
        "des noel, ou un zephyr hai me vet de glacons wuermiens, je dine d’exquis rotis de boeuf au kir, a l’ay d’age mur, &caetera.",
    ),
    (
        "Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.",
        "falsches ueben von xylophonmusik quaelt jeden groesseren zwerg.",
    ),
    (
        "Љубазни фењерџија чађавог лица хоће да ми покаже штос.",
        "љубазни фењерџија чађавог лица хоће да ми покаже штос.",
    ),
    (
        "Ljubazni fenjerdžija čađavog lica hoće da mi pokaže štos.",
        "ljubazni fenjerdzija cadavog lica hoce da mi pokaze stos.",
    ),
    (
        "Quizdeltagerne spiste jordbær med fløde, mens cirkusklovnen Walther spillede på xylofon.",
        "quizdeltagerne spiste jordbaer med flode, mens cirkusklovnen walther spillede pa xylofon.",
    ),
    (
        "Kæmi ný öxi hér ykist þjófum nú bæði víl og ádrepa.",
        "kaemi ny oexi her ykist þjofum nu baedi vil og adrepa.",
    ),
    (
        "Glāžšķūņa rūķīši dzērumā čiepj Baha koncertflīģeļu vākus.",
        "glazskuna rukisi dzeruma ciepj baha koncertfligelu vakus.",
    )
]


@pytest.mark.parametrize("text, expected", remove_diacritics_data)
def test_remove_diacritics(text, expected):
    result = remove_diacritics(text)
    print(result)
    assert result == expected


string_to_pairs_data = [
    ("", []),
    ("123", [("", 123)]),
    ("abc", [("abc", 0)]),
    ("123abc", [("", 123), ("abc", 0)]),
    ("abc123", [("abc", 123)]),
    ("123abc456", [("", 123), ("abc", 456)]),
    ("abc123efg", [("abc", 123), ("efg", 0)]),
]


@pytest.mark.parametrize("string, expected", string_to_pairs_data)
def test_string_to_pairs(string, expected):
    result = string_to_pairs(string)
    print(result)
    assert result == expected


# Some extracts from the test suite of the natsort library. Permalink:
# https://github.com/SethMMorton/natsort/blob/e3c32f5638bf3a0e9a23633495269bea0e75d379/tests/test_natsorted.py

sort_data = [
    (  # same as test_natsorted_can_sort_as_unsigned_ints_which_is_default()
        ["a50", "a51.", "a50.31", "a-50", "a50.4", "a5.034e1", "a50.300"],
        ["a5.034e1", "a50", "a50.4", "a50.31", "a50.300", "a51.", "a-50"],
    ),
    (  # same as test_natsorted_numbers_in_ascending_order()
        ["a2", "a5", "a9", "a1", "a4", "a10", "a6"],
        ["a1", "a2", "a4", "a5", "a6", "a9", "a10"],
    ),
    (  # same as test_natsorted_can_sort_as_version_numbers()
        ["1.9.9a", "1.11", "1.9.9b", "1.11.4", "1.10.1"],
        ["1.9.9a", "1.9.9b", "1.10.1", "1.11", "1.11.4"],
    ),
    (  # different from test_natsorted_handles_filesystem_paths()
        [
            "/p/Folder (10)/file.tar.gz",
            "/p/Folder (1)/file (1).tar.gz",
            "/p/Folder/file.x1.9.tar.gz",
            "/p/Folder (1)/file.tar.gz",
            "/p/Folder/file.x1.10.tar.gz",
        ],
        [
            "/p/Folder (1)/file (1).tar.gz",
            "/p/Folder (1)/file.tar.gz",
            "/p/Folder (10)/file.tar.gz",
            "/p/Folder/file.x1.9.tar.gz",
            "/p/Folder/file.x1.10.tar.gz",
        ],
    ),
    (  # same as test_natsorted_path_extensions_heuristic()
        [
            "Try.Me.Bug - 09 - One.Two.Three.[text].mkv",
            "Try.Me.Bug - 07 - One.Two.5.[text].mkv",
            "Try.Me.Bug - 08 - One.Two.Three[text].mkv",
        ],
        [
            "Try.Me.Bug - 07 - One.Two.5.[text].mkv",
            "Try.Me.Bug - 08 - One.Two.Three[text].mkv",
            "Try.Me.Bug - 09 - One.Two.Three.[text].mkv",
        ],
    ),
    (  # same as ns.DEFAULT for test_natsorted_supports_case_handling()
        ["Apple", "corn", "Corn", "Banana", "apple", "banana"],
        ["Apple", "Banana", "Corn", "apple", "banana", "corn"],
    ),
]


@pytest.mark.parametrize("given, expected", sort_data)
def test_string_to_pairs_as_sort_key(given, expected):
    result = sorted(given, key=string_to_pairs)
    print(result)
    assert result == expected


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
