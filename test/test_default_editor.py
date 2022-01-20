import pytest
from platform import platform as get_platform_string

import context
from src.default_editor import *


def test_get_editor_command():
    os_name = get_platform_string().split("-")[0]
    if os_name not in ("Linux", "macOS"):
        with pytest.raises(UnsupportedOSError):
            get_editor_command(os_name)
    else:
        command = get_editor_command(os_name)
        assert command[0] in ("code", "subl", "open")


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
