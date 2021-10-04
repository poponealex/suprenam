import pytest
from platform import platform

import context
from src.default_editor import *


def test_get_editor_command_name():
    os = platform().split("-")[0]
    if os != "Linux" and os != "macOS":
        with pytest.raises(UnsupportedOS):
            get_editor_command_name(os)
    else:
        result = get_editor_command_name(os)
        assert result[0] in ("code", "subl", "open")


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
