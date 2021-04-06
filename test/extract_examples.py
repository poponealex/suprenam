from pathlib import Path
import re
import context
from src.goodies import print_warning

SECTION_PATTERN = r"""(?m)^### (.+)\n
#### Example\n
original path \| new name
---\|---
((?:.+\n)*)
#### Result\n
original path \| new path
---\|---
((?:.+\n)*)"""


def extract_rows(table):
    if not table:
        return []
    return [tuple(row.split("|")) for row in table.strip().split("\n")]


def main(path):
    result = []
    text = path.read_text()
    for match in re.finditer(SECTION_PATTERN, text):
        (title, example, expected) = match.groups()
        result.append(
            {
                "title": title,
                "example": extract_rows(example),
                "expected": extract_rows(expected),
            }
        )
    if len(result) < len(re.findall("(?m)^### ", text)):
        print_warning('"examples.md" has more sections than matches.')
    return result


if __name__ == "__main__":
    for (i, test_data) in enumerate(main(Path("test/examples.md")), 1):
        test_data["#"] = i
        print("Section {#}: {title}".format(**test_data))
        print("Example: {example}".format(**test_data))
        print("Expected: {expected}".format(**test_data))
