from pathlib import Path


def get_path_siblings(paths: set[Path]) -> set[Path]:
    result = set()
    for path in paths:
        if path not in result:
            for p in Path(path.parent).glob("*"):
                result.add(p)
    return result
