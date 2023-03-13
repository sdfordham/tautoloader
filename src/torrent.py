import re
from pathlib import Path
from difflib import get_close_matches
from typing import Optional, Union


class TorrentData:
    def __init__(self, path: Path, **kwargs) -> None:
        if self._is_torrent_file(path):
            self.path: Path = path
        else:
            raise ValueError(f"Not a torrent file: {path}")
        self.data: Optional[list[Path]] = kwargs.get("data", None)
        self.tracker: Optional[str] = self.guess_tracker(path, **kwargs)

    def __str__(self) -> str:
        obj_vals = {
            "path": str(self.path),
        }
        if self.data:
            if isinstance(self.find_data, Path):
                obj_vals["data"] = str(self.data)
            else:
                obj_vals["data"] = [str(s) for s in self.data]
        if self.tracker:
            obj_vals["tracker"] = self.tracker
        return (
            f"TorrentFile(" + ", ".join([f"{k}={v}" for k, v in obj_vals.items()]) + ")"
        )

    @staticmethod
    def _is_torrent_file(path: Path) -> bool:
        if not path.is_file() or not path.suffix == ".torrent":
            return False
        return True

    def find_data(
        self, files: list[Path], cutoff: float = 0.9
    ) -> Optional[Union[Path, list[Path]]]:
        stems_hash = {ff.stem: ff for ff in files}
        close_matches = get_close_matches(
            word=self.path.stem, possibilities=stems_hash.keys(), cutoff=cutoff
        )
        if close_matches:
            close_matches = [stems_hash[s] for s in close_matches]
        self.data = close_matches

    @staticmethod
    def guess_tracker(path, read_len: int = 100) -> Optional[str]:
        with open(path, "rb") as F:
            line = F.readline()
            try:
                line_decoded = line[:read_len].decode("utf-8")
            except UnicodeDecodeError:
                return None
            tracker = re.match(
                r"^[\w]*:announce[0-9]*:http:\/\/([\w.-]+)", line_decoded
            )
        if tracker:
            return tracker.group(1)
        return None
