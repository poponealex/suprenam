import pytest

import context
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


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
