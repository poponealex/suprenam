import pytest

__import__("sys").path[0:0] = "."
from src.context import Context
from src.get_editor_command import *


def test_when_favorite_editor_is_set():
    config_path = Path("test") / "workspace" / "config.json"
    config_path.write_text('{"editor_command": "mock_favorite_command"}')
    context = Context("mockOS")
    assert get_editor_command(context, Path("foobar")) == "mock_favorite_command foobar"


def test_with_unsupported_platform():
    with pytest.raises(UnsupportedOSError):
        get_editor_command(Context("MS-DOS"), Path("foobar"))


def test_with_mock_os():
    config_path = Path("test") / "workspace" / "config.json"
    if config_path.exists():
        config_path.unlink()  # Python 3.8 and newer: use `missing_ok`` parameter.
    context = Context("mockOS")
    assert get_editor_command(context, Path("foobar")) == "mock_default_command foobar"


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
