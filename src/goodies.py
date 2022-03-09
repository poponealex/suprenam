import re
from pathlib import Path
from unicodedata import combining, normalize

LATIN = "ä  æ  ǽ  đ ð ƒ ħ ı ł ø ǿ ö  œ  ß  ŧ ü "
ASCII = "ae ae ae d d f h i l o o oe oe ss t ue"


def remove_diacritics(s: str, outliers=str.maketrans(dict(zip(LATIN.split(), ASCII.split())))):
    return "".join(c for c in normalize("NFD", s.lower().translate(outliers)) if not combining(c))


def string_to_pairs(s, pairs=re.compile(r"(\D*)(\d*)").findall):
    return [(text, int(digits or 0)) for (text, digits) in pairs(s)[:-1]]


def rm_tree(path: Path):  # https://stackoverflow.com/a/57892171/173003
    if not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()
