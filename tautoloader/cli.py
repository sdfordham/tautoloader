import re
import time
from getpass import getpass
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from .torrent import TorrentData
from .transmission import TransmissionCommand
from .methods import find_files, parse_list_output


def main(
    torrent_folder: Path,
    data_folder: Path,
    exclude_tracker: Optional[str],
    username: Optional[str],
    password: Optional[str],
    sleep: int,
    cutoff: float,
    prompt: bool
):
    # Get the files
    torrent_files = [
        TorrentData(f) for f in find_files(torrent_folder, valid_exts=[".torrent"])
    ]
    data_files = find_files(data_folder, exclude_exts=[".torrent"])

    # Get the output from the client
    cmd = TransmissionCommand()
    if username and password:
        cmd.auth(username, password)
    cmd.list()
    res = cmd.exec()
    client_output = parse_list_output(res)

    res = None
    for tf in torrent_files:
        if exclude_tracker and (
            tf.tracker is None or re.match(exclude_tracker, tf.tracker)
        ):
            continue
        tf.find_data(data_files, cutoff)

        if tf.data:
            print(f"Torrent file @ {tf.path}\n  from tracker {tf.tracker}")

            if len(tf.data) == 1:
                download_dir = tf.data[0].parent
                print(f"matched data @ {download_dir}")
            elif len(tf.data) > 1:
                uniq_parents = {f.parent for f in tf.data}
                if len(uniq_parents) == 1:
                    print(f"matched data @ {tf.data[0].parent}")
                    download_dir = tf.data[0].parent
                else:
                    print(f"matched data @ (multiple locations)")
                    for idx, f in enumerate(uniq_parents):
                        print(f"             {idx}. {f}")
                    download_dir = None

            cmd = TransmissionCommand()
            if username and password:
                cmd.auth(username, password)
            cmd.add(tf.path)

            if not prompt and download_dir:
                cmd.download_dir(download_dir)
                res = cmd.exec()
            else:
                print("Add to transmission?")
                inp = input("1. Yes, 2. No, 3. Provide download directory\n")
                if inp.strip('.') == '1' and download_dir:
                    cmd.download_dir(download_dir)
                    res = cmd.exec()
                elif inp.strip('.') == '2':
                    continue
                elif inp.strip('.') == '3':
                    inp = input("Enter download directory: ")
                    if Path(inp).is_dir():
                        cmd.download_directory(inp)
                        res = cmd.exec()
                    else:
                        raise ValueError("Directory does nae exist.")
                else:
                    raise ValueError("Invalid option and/or no download directory.")

            print("Transmission response:", res)
            time.sleep(sleep)
        else:
            print("No torrent data found for", tf)


if __name__ == "__main__":
    parser = ArgumentParser(prog="transmission autoloader")
    parser.add_argument("-t", "--torrent_folder", type=Path, required=True)
    parser.add_argument("-d", "--data_folder", type=Path, required=True)
    parser.add_argument("-e", "--exclude_tracker", type=str, default=None)
    parser.add_argument("-u", "--username", type=str, default=None)
    parser.add_argument("-s", "--sleep", type=int, default=5)
    parser.add_argument("-c", "--cutoff", type=float, default=0.9)
    parser.add_argument("-p", "--prompt", type=bool, default=True)
    args = vars(parser.parse_args())

    args["password"] = getpass() if args["username"] else None
    main(**args)
