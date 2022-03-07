import pytest

import context
from src.get_editor_command import *


def test_when_default_editor_is_set():
    path = Path.home() / ".suprenam" / "MOCK_DEFAULT_EDITOR_YES"
    path.write_text("foo")
    assert (
        get_editor_command(
            Path("bar"),
            default_editor="MOCK_DEFAULT_EDITOR_YES",
            platform="mockOS",
        )
        == "foo bar"
    )
    path.unlink()


def test_with_unsupported_platform():
    with pytest.raises(UnsupportedOSError):
        get_editor_command(
            Path("foobar"),
            default_editor="MOCK_DEFAULT_EDITOR_NO",
            platform="MS-DOS",
        )


def test_with_mock_os():
    assert (
        get_editor_command(
            Path("foobar"),
            default_editor="MOCK_DEFAULT_EDITOR_NO",
            platform="mockOS",
        )
        == "mock_command foobar"
    )


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
