import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Union

from cx_Freeze import Executable, setup

EXCLUDES = ["matplotlib.tests", "numpy.random._examples"]
INCLUDE_FILES: List[Tuple[Union[str, Path], Union[str, Path]]] = [
    ("resources/readme.txt", "components/readme.txt"),
    ("resources/icon.ico", "resources/icon.ico"),
    ("resources/config.toml", "config.toml"),
]
ZIP_INCLUDE_PACKAGES = []

COPIED = []
TO_COPY = {}

try:
    base_interpretter = sys.real_prefix  # type: ignore
except AttributeError:
    pass
else:
    # In a virtualenv
    base_interpretter = sys.real_prefix  # type: ignore
    SRC_PATH = Path(base_interpretter)
    DEST_PATH = Path(sys.executable).parent.parent

    EXCLUDES.append("site")
    INCLUDE_FILES.append((SRC_PATH / "Lib" / "site.py", Path("lib") / "site.py"))
    INCLUDE_FILES.append((SRC_PATH / "Lib" / "_sitebuiltins.py", Path("lib") / "_sitebuiltins.py"))

    ZIP_INCLUDE_PACKAGES.append("distutils")
    SRC_DISTUTILS = SRC_PATH / "Lib" / "distutils"
    DEST_DISTUTILS = DEST_PATH / "Lib" / "distutils"
    for name in os.listdir(SRC_DISTUTILS):
        TO_COPY[SRC_DISTUTILS / name] = DEST_DISTUTILS / name

    TO_COPY[SRC_PATH / "DLLs"] = DEST_PATH / "DLLs"

    for src, dest in TO_COPY.items():
        if not os.path.exists(dest):
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dest)
                else:
                    shutil.copy(src, dest)
            except PermissionError:
                print(f"No permission to copy from {src!r} to {dest!r}")
            else:
                COPIED.append(dest)

try:
    setup(
        name="Spotify Analyzer",
        version="0.1",
        description="My GUI application!",
        options={
            "build_exe": {
                "packages": ["numpy", "scipy", "tkinter"],
                "excludes": EXCLUDES,
                "include_files": INCLUDE_FILES,
                "zip_include_packages": ZIP_INCLUDE_PACKAGES,
            }
        },
        executables=[
            Executable("src/main.py", base="Win32GUI", targetName="spotify-analyzer.exe", icon="resources/icon.ico")
        ],
    )
finally:
    for path in COPIED:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
