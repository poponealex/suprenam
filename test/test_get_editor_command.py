import pytest

import context
from src.get_editor_command import *


def test_get_editor_command_with_explicit_current_platform():
    platform = get_platform_long_string().partition("-")[0]
    command = get_editor_command(Path("foobar"), platform)
    assert command[0] in ["code", "subl", "open"]


def test_get_editor_command_with_detected_current_platform():
    command = get_editor_command(Path("foobar"))
    assert command[0] in ["code", "subl", "open"]


def test_get_editor_command_with_explicit_not_supported_platform():
    with pytest.raises(UnsupportedOSError):
        get_editor_command(Path("foobar"), "Windows")


def test_get_editor_command_with_explicit_wrong_platform():
    platform = get_platform_long_string().partition("-")[0]
    with pytest.raises(Exception):
        get_editor_command(Path("foobar"), "macOS" if platform == "Linux" else "Linux")


if __name__ == "__main__":  # pragma: no cover
    pytest.main(["-qq", __import__("sys").argv[0]])
