import re
import time
from getpass import getpass
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from transmission import TransmissionCommand


def main(
    torrent_folder: Path,
    data_folder: Path,
    exclude_tracker: Optional[str],
    username: Optional[str],
    password: Optional[str],
    sleep: int,
):
    torrent_files = [
        TorrentData(f) for f in find_files(torrent_folder, valid_exts=[".torrent"])
    ]
    data_files = find_files(data_folder, exclude_exts=[".torrent"])
    for tf in torrent_files:
        if exclude_tracker and (
            tf.tracker is None or re.match(exclude_tracker, tf.tracker)
        ):
            continue
        tf.find_data(data_files)
        if tf.data:
            print(f"Torrent file @ {tf.path}\n  from tracker {tf.tracker}")
            if len(tf.data) == 1:
                download_dir = tf.data[0].parent
                print(f"matched data @ {download_dir}\nAdding to transmission...")
                
                cmd = TransmissionCommand()
                if username and password:
                    cmd.auth(username, password)
                cmd.add(tf.path).download_dir(download_dir)
                res = cmd.exec()
                print("Transmission response:", res)
                
                time.sleep(sleep)
            elif len(tf.data) > 1:
                uniq_parents = {f.parent for f in tf.data}
                if len(uniq_parents) == 1:
                    print(f"matched data @ {tf.data[0].parent}")
                else:
                    print(f"matched data @ (multiple locations, skipping)")
                    for idx, f in enumerate(uniq_parents):
                        print(f"             {idx}. {f}")
            print("\n    ============    \n")


if __name__ == "__main__":
    parser = ArgumentParser(prog="transmission autoloader")
    parser.add_argument("-t", "--torrent_folder", type=Path)
    parser.add_argument("-d", "--data_folder", type=Path)
    parser.add_argument("-e", "--exclude_tracker", type=str, default=None)
    parser.add_argument("-u", "--username", type=str, default=None)
    parser.add_argument("-s", "--sleep", type=int, default=5)
    args = vars(parser.parse_args())

    args["password"] = getpass() if args["username"] else None
    main(**args)
