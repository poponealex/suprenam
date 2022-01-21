import pytest
from platform import platform as get_platform_string

import context
from src.get_editor_command import *


def test_get_editor_command():
    platform_string = get_platform_string().split("-")[0]
    if platform_string not in ("Linux", "macOS"):
        with pytest.raises(UnsupportedOSError):
            get_editor_command(Path("foobar"))
    else:
        command = get_editor_command(Path("foobar"))
        assert command[0] in ("code", "subl", "open")


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
