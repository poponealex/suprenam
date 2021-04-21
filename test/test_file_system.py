import pytest

from pathlib import Path

import context
from src.file_system import FileSystem


@pytest.fixture(scope="module")
def base_path():
    return Path(".").resolve()

@pytest.fixture()
def paths(base_path):
    return [
        str(base_path / "src" / "goodies.py"),
        str(base_path / "src" / "goodies.py"), # duplicates don't matter
        str(base_path / "test" / "context.py"),
    ]

def test_constructor(base_path, paths):
    fs = FileSystem(paths)
    assert Path(base_path / "src" / "goodies.py") in fs
    assert Path(base_path / "test" / "context.py") in fs
    assert Path(base_path / "src" / "file_system.py") in fs
    assert Path(base_path / "src") not in fs

def test_failed_constructor(base_path, paths):
    paths.append(Path(base_path / "non_existing_node"))
    with pytest.raises(FileNotFoundError):
        fs = FileSystem(paths)

if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
