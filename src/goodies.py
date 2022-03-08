import re
from pathlib import Path
from unicodedata import normalize, combining

OUTLIERS = str.maketrans(
    {
        "ä": "ae",
        "æ": "ae",
        "ǽ": "ae",
        "đ": "d",
        "ð": "d",
        "ƒ": "f",
        "ħ": "h",
        "ı": "i",
        "ł": "l",
        "ø": "o",
        "ǿ": "o",
        "ö": "oe",
        "œ": "oe",
        "ß": "ss",
        "ŧ": "t",
        "ü": "ue",
    }
)


def remove_diacritics(s):
    return "".join(c for c in normalize("NFD", s.lower().translate(OUTLIERS)) if not combining(c))


def string_to_pairs(s, texts_and_nats=re.compile(r"(\D*)(\d*)").findall):
    return [(txt, int(nat or 0)) for (txt, nat) in texts_and_nats(s)][:-1]


def rm_tree(path: Path):  # https://stackoverflow.com/a/57892171/173003
    if not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()
