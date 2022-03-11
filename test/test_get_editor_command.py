import pytest

__import__("sys").path[0:0] = "."
from src.context import Context
from src.get_editor_command import *


def test_when_favorite_editor_is_set():
    context = Context("mockOS")
    path = context.workspace / "FAVORITE_EDITOR"
    path.write_text("foo")
    assert get_editor_command(context, Path("bar")) == "foo bar"


def test_with_unsupported_platform():
    with pytest.raises(UnsupportedOSError):
        get_editor_command(Context("MS-DOS"), Path("foobar"))


def test_with_mock_os():
    context = Context("mockOS")
    assert (
        get_editor_command(
            context,
            Path("foobar"),
            favorite_editor_filename="NOT_EXISTING_FILE",
        )
        == "mock_command foobar"
    )


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
