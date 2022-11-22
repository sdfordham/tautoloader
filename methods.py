import re
import subprocess
from pathlib import Path
from typing import Optional

from .transmission import TransmissionRow


def find_files(
    folder: Path,
    ignore_permission_err: bool = True,
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


def add_to_transmission(
    add: Path,
    download_dir: Path,
    username: Optional[str] = None,
    password: Optional[str] = None,
):
    args = [
        "transmission-remote",
        "--add",
        str(add),
        "--download-dir",
        str(download_dir),
    ]
    if username and password:
        args.append("--auth")
        args.append(username + ":" + password)

    cp = subprocess.run(
        args=args,
        capture_output=True,
        check=True,
    )
    return cp.stdout


def parse_list_output(output: bytes) -> list[TransmissionRow]:
    decoded = output.decode("utf-8").strip().split("\n")
    lines = [re.split(r"\s[\s]+", line.strip()) for line in decoded]
    return [TransmissionRow(*l) for l in lines]
