import os
import setuptools
from pathlib import Path
from time import time

setuptools.setup(
    name="suprenam",
    version=os.environ.get("RELEASE_VERSION") if os.environ.get("RELEASE_VERSION") != "main" else f"0.9.9-beta.{int(time())}",
    author="Aristide Grange & Alexandre Perlmutter",
    author_email="alexandre.perlmutter@gmail.com",
    description="Easily rename files and folders via your favorite text editor.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/poponealex/suprenam",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=['src', 'src.*']),
    python_requires=">=3.6",
    install_requires=Path("requirements.txt").read_text().split("\n")[:-1],
    entry_points={"console_scripts": ["suprenam=src.suprenam:main_wrapper"]},
)
