import pytest

from pathlib import Path

import context
from src.renamer import check_and_complete


@pytest.fixture(scope="module")
def base_path():
    return Path(".").resolve()


@pytest.fixture()
def paths(base_path):
    return [
        base_path / "src" / "goodies.py",
        base_path / "src" / "goodies.py",  # duplicates don't matter
        base_path / "test" / "context.py",
    ]


def test_check_and_complete(base_path, paths):
    result = check_and_complete(paths)
    assert Path(base_path / "src" / "goodies.py") in result
    assert Path(base_path / "test" / "context.py") in result
    assert Path(base_path / "src" / "file_system.py") in result
    assert Path(base_path / "src") not in result


def test_check_and_complete_failed(base_path, paths):
    paths.append(Path(base_path / "non_existing_node"))
    with pytest.raises(FileNotFoundError):
        result = check_and_complete(paths)


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
