"""
Read the contents of test/examples.md, normalize its formatting and write it back.

The following operations are carried out:

- The old clickable table of contents (if any) is replaced by a new one.
- The spaces and separators between sections are homogeneized.

This code is executed each time test/test_examples.py is called. Thus, although no
unit test is provided, any regression should be visible in the differences between
two versions of test/example.md.
"""

from collections import defaultdict
import re
from pathlib import Path
from typing import Callable
from unicodedata import normalize


def title_to_slug_factory() -> Callable:
    """Return a function mapping a string to the appropriate slug, optionally disambiguated.

    Returns:
        Callable[[str, Optional[bool]]]: A function taking a string and an optional boolean
            `deduplicate` (default: `False`). If `True`, when two or more strings produce the same
            slug, a numeric suffix is added to the second one (`"-1"`), the third one (`"-2"`), and
            so on.

    Remark:
        This function is extracted from (and tested in) Paroxython.
        https://github.com/laowantong/paroxython/blob/4626798a60eeaa765dbfab9e63e04030c9fcb1d0/paroxython/goodies.py#L21-L53
    """
    slug_counts: Dict[str, int] = defaultdict(int)
    cache: Dict[str, str] = {}

    def title_to_slug(title, deduplicate=False):
        title = title.strip()
        if title not in cache:
            slug = normalize("NFD", title.lower()).encode("ASCII", "ignore").decode("ASCII")
            slug = slug.replace(" ", "-")
            slug = re.sub(r"[^\w-]", "", slug)
            cache[title] = slug
        if deduplicate:
            slug = cache[title]
            slug_counts[slug] += 1
            slug = f"{slug}-{slug_counts[slug] - 1}"
            slug_counts[slug] += 1
            slug = slug.rstrip("-0")
            return slug
        else:
            return cache[title]

    return title_to_slug


title_to_slug = title_to_slug_factory()


def generate_toc(text):
    for match in re.finditer(r"(?m)^(#{1,3}) (.+)", text):
        (hashtags, title) = match.groups()
        offset = "  " * (len(hashtags) - 1) + "- "
        slug = title_to_slug(title, deduplicate=True)
        yield f"{offset}[{title}](#{slug})"


def main(path):
    text = path.read_text()
    toc = "\n".join(generate_toc(text))
    rule = "-" * 80 + "\n"
    text = re.sub(r"(?m)^---+\n", "", text)
    text = re.sub(r"(?m)^ +```", "```", text)
    text = re.sub(r"(?ms).*?^(?=# )", fr"{toc}\n\n", text, count=1)
    text = re.sub(r"(?m)\s+^(#+ .+)\s+", fr"\n\n\1\n\n", text)
    # text = re.sub(r"(?ms)^(\| Label \| .+?)(^\#{1,3} )", fr"\1{rule}\n\2", text)
    text = re.sub(r"(?=\n\#{3} )", fr"\n{rule}", text)
    path.write_text(text)


if __name__ == "__main__":
    main(Path("test/examples.md"))
