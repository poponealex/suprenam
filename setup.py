import os
import setuptools
from pathlib import Path

setuptools.setup(
    name="suprenam",
    version=os.environ.get("RELEASE_VERSION") if os.environ.get("RELEASE_VERSION") != "main" else "0.9.9-beta.1",
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
    package_dir={"src": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
