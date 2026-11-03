"""Build on each target OS/architecture; never cross-compile Python binaries."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "open-notebook-api",
        "--paths",
        str(root / "apps/api"),
        "--distpath",
        str(root / "build/backend"),
        "--workpath",
        str(root / "build/pyinstaller"),
        "--specpath",
        str(root / "build"),
        "--collect-submodules",
        "keyring.backends",
        "--collect-submodules",
        "mcp.server",
        "--collect-data",
        "certifi",
        "--collect-data",
        "pptx",
        "--collect-data",
        "reportlab",
        "--collect-submodules",
        "fontTools.ttLib.tables",
        "--add-data",
        str(root / "apps/api/on_knowledge/features/presentations/fonts")
        + os.pathsep
        + "on_knowledge/features/presentations/fonts",
        "--copy-metadata",
        "cryptography",
        "--copy-metadata",
        "python-pptx",
        "--copy-metadata",
        "reportlab",
        "--copy-metadata",
        "fonttools",
        "--copy-metadata",
        "xlsxwriter",
        str(root / "apps/api/run.py"),
    ],
    cwd=root,
    check=True,
)

if notice := os.environ.get("RACALL_OPENSSL_NOTICE"):
    source = Path(notice)
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("The linked OpenSSL copyright/license notice is missing.")
    legal = root / "build/backend/open-notebook-api/legal"
    legal.mkdir(exist_ok=True)
    shutil.copyfile(source, legal / "OPENSSL.txt")
