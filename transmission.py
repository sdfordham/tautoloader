import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


class TransmissionCommand:
    def __init__(self):
        self.args = ["transmission-remote"]

    def add(self, path: Path) -> "TransmissionCommand":
        self.args.append("--add")
        self.args.append(str(path))
        return self

    def download_dir(self, path: Path) -> "TransmissionCommand":
        self.args.append("--download-dir")
        self.args.append(str(path))
        return self

    def auth(self, username: str, password: str) -> "TransmissionCommand":
        self.args.append("--auth")
        self.args.append(username + ":" + password)
        return self

    def list(self) -> "TransmissionCommand":
        self.args.append("-l")
        return self

    def exec(self) -> str:
        cp = subprocess.run(
            self.args,
            capture_output=True,
            check=True
        )
        return cp.stdout


@dataclass
class TransmissionRow:
    id_: Optional[str] = None
    done: Optional[str] = None
    have: Optional[str] = None
    eta: Optional[str] = None
    up: Optional[str] = None
    down: Optional[str] = None
    ratio: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None