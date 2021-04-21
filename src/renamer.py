from src.file_system import FileSystem


def check_and_complete(paths):
    """Check that all the given paths exist, and add all the other children of their parents."""
    result = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError
        result.update(path.parent.glob("*"))
    return result

