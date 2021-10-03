import pytest
from platform import platform

import context
from src.default_editor import *


def test_get_editor_command():
    os = platform().split("-")[0]
    if os != "Linux" and os != "macOS":
        with pytest.raises(UnsupportedOS):
            get_editor_command(os)
    else:
        result = get_editor_command(os)
        if os == "macOS":
            assert result[0] in ("/usr/local/bin/code", "/usr/local/bin/subl", "/usr/bin/open")
        elif os == "Linux":
            assert result[0] in ("/bin/open", "/usr/bin/code", "/usr/bin/subl")


if __name__ == "__main__":
    pytest.main(["-qq", __import__("sys").argv[0]])
