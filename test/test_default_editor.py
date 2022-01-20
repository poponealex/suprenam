import pytest
from platform import platform

import context
from src.default_editor import *


def test_get_editor_command():
    os_name = platform().split("-")[0]
    if os_name not in ("Linux", "macOS"):
        with pytest.raises(UnsupportedOSError):
            get_editor_command(os_name)
    else:
        command = get_editor_command(os_name)
        assert command[0] in ("code", "subl", "open")


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
