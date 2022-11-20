import subprocess
import re
import time
from getpass import getpass
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional


def find_files(
    folder: Path,
    ignore_permission_err=True,
    valid_exts: Optional[list[str]] = None,
    exclude_exts: Optional[list[str]] = None,
) -> list[Path]:
    files = list()
    for path in folder.glob("**/"):
        try:
            for f in path.iterdir():
                if f.is_file():
                    if valid_exts and f.suffix not in valid_exts:
                        continue
                    if exclude_exts and f.suffix in exclude_exts:
                        continue
                    files.append(f)
        except PermissionError as e:
            if not ignore_permission_err:
                raise e
    return files


def add_to_transmission(add: Path, download_dir: Path, username: str, password: str):
    cp = subprocess.run(
        [
            "transmission-remote",
            "--add",
            str(add),
            "--download-dir",
            str(download_dir),
            "--auth",
            username + ":" + password,
        ],
        capture_output=True,
        check=True,
    )
    return cp.stdout