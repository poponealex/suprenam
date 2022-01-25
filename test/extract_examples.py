from pathlib import Path
import re
import context

SECTION_PATTERN = r"""(?m)^### (.+)\n
#### Example\n
original path \| new name
---\|---
((?:.+\n)*)
#### Result\n
(?:original path \| new path
---\|---\n)?((?:.+\n)*)"""


def extract_rows(table):
    if not table:
        return []
    m = re.match(r"`(\w+Error)\(\"(.+)\"\)`\n", table)
    if m:
        return (m[1], m[2])
    return [tuple([x.strip() for x in row.split("|")]) for row in table.strip().split("\n")]


def extract_examples(path):
    result = []
    text = path.read_text()
    for (i, match) in enumerate(re.finditer(SECTION_PATTERN, text), 1):
        (title, example, expected) = match.groups()
        result.append(
            {
                "i": i,
                "title": title,
                "example": extract_rows(example),
                "expected": extract_rows(expected),
            }
        )
    if len(result) < len(re.findall("(?m)^### ", text)):  # pragma: no cover
        raise ValueError("examples.md has more sections than matches.")
    return result


if __name__ == "__main__":  # pragma: no cover
    for (i, test_data) in enumerate(extract_examples(Path("test/examples.md")), 1):
        print("Section {i}: {title}".format(**test_data))
        print("Example: {example}".format(**test_data))
        print("Expected: {expected}".format(**test_data))
