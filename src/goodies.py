from pathlib import Path


def rm_tree(path: Path):  # https://stackoverflow.com/a/57892171/173003
    if not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()
