from pathlib import Path


def get_path_siblings(paths: set[Path]) -> set[Path]:
    acc = set()
    for path in paths:
        if path not in acc:
            for p in Path(path.parent).glob("*"):
                acc.add(p)
    return paths.union(acc)
