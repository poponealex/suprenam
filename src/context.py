from platform import platform as get_platform_long_string
from pathlib import Path

from src.user_errors import *
from src.logger import Logger
from src.printer import ColorPrinter, PlatypusPrinter


class Context:
    def __init__(self, platform_name: str = "", full=True):
        """
        Set up the platform and, if needed, create the Suprenam's data folder.

        Args:
            platform: the current OS, only provided during testing.
        Raises:
            UnsupportedOSError: if the OS is not in self.SUPPORTED_OS.
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
        
        if not full:
            return

        self.workspace.mkdir(
            parents=True,  # any missing parents of this path are created as needed
            exist_ok=True,  # if the directory already exists, do not raise an exception
        )
        self.logger = Logger(self.workspace)

        self.print_ = ColorPrinter(self)
        if Path.cwd().name == "Resources":
            # We are in the app bundle (macOS)
            self.print_ = PlatypusPrinter(self)  # type: ignore


if __name__ == "__main__":
    context = Context(full=False)
    log_file = context.workspace / "log.txt"
    print(int(log_file.is_file()))
