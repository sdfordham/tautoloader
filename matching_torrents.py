import re
from typing import Optional, Union
from pathlib import Path
from difflib import get_close_matches


class TFDataFinder:
    def __init__(self, path: Path, **kwargs) -> None:
        if self._is_torrent_file(path):
            self.path: Path = path
        else:
            raise ValueError(f"Not a torrent file: {path}")
        self.data: Optional[Union[Path, list[Path]]] = kwargs.get("data", None)
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
        self.data = close_matches if len(close_matches) > 1 else close_matches[0]

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
        return tracker


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


def main():
    TORRENT_FOLDER = Path("V:\\")
    DATA_FOLDER = Path("V:\\")

    torrent_files = [
        TFDataFinder(f) for f in find_files(TORRENT_FOLDER, valid_exts=[".torrent"])
    ]
    data_files = find_files(DATA_FOLDER, exclude_exts=[".torrent"])
    for tf in torrent_files:
        tf.find_data(data_files)
        print(tf)


if __name__ == "__main__":
    main()
