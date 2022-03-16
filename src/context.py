from platform import platform as get_platform_long_string
from pathlib import Path
import json

from src.user_errors import *
from src.logger import Logger
from src.printer import Printer


class Context:

    DEFAULT_CONFIG = {
        "editor_command": "",
        "logs_to_keep": 10,
    }

    def __init__(self, platform_name: str = "", full=True):
        """
        Set up the platform and, if needed, create the Suprenam's data folder.

        Args:
            platform: the current OS, only provided during testing.
        Raises:
            UnsupportedOSError: if the current OS is not supported.
        """
        self.platform = platform_name or get_platform_long_string().partition("-")[0]

        if self.platform == "macOS":
            self.workspace = Path.home() / "Library" / "Application Support" / "Suprenam"
        elif self.platform == "Linux":
            self.workspace = Path.home() / ".suprenam"
        elif self.platform == "Windows":
            self.workspace = Path.home() / "AppData" / "Roaming" / "Suprenam"
        elif self.platform == "mockOS":
            self.workspace = Path("test") / "workspace"
        else:
            raise UnsupportedOSError(f"Unsupported operating system: {self.platform}.")

        self.workspace.mkdir(
            parents=True,  # any missing parents of this path are created as needed
            exist_ok=True,  # if the directory already exists, do not raise an exception
        )

        config_path = self.workspace / "config.json"
        if not config_path.is_file():
            config_path.write_text(json.dumps(self.DEFAULT_CONFIG, indent=4))
        self.config = json.loads(config_path.read_text())

        self.logger = Logger(self)

        self.print_ = Printer(self)
