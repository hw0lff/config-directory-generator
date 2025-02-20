#!/usr/bin/env python3
# SPDX-License-Identifier: EUPL-1.2

from pathlib import Path
from dataclasses import dataclass
import argparse


@dataclass
class DropInConfiguration:
    drop_in_dir: Path
    runtime_dir: Path
    runtime_file: str
    add_file_name_comment: str | None

    @property
    def runtime_config_file_path(self) -> Path:
        return self.runtime_dir / f"{self.runtime_file}"

    def generate_config_content(self) -> str:
        file_paths = []
        for root, dirs, dir_files in self.drop_in_dir.walk():
            dir_files = list(dir_files)
            dir_files.sort()
            for file in dir_files:
                if (root / file).is_file():
                    file_paths.append(root / file)
        if self.add_file_name_comment is not None:
            file_contents = (
                self.add_file_name_comment + " " + f.name + "\n" + f.read_text()
                for f in file_paths
            )
        else:
            file_contents = (f.read_text() for f in file_paths)
        config_content = "\n".join(file_contents)
        return config_content

    def write_runtime_config_file(self):
        config_content: str = self.generate_config_content()

        fpath: Path = self.runtime_config_file_path
        fpath.unlink(missing_ok=True)
        fpath.touch(mode=0o600)
        with open(fpath, mode="w") as config_file:
            fpath.chmod(mode=0o400)
            # assert that it is only readable by user before writing
            assert ((fpath.stat().st_mode & 0o777) ^ 0o400) == 0
            config_file.write(config_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="concatenates every file in the drop-in directory to a single file in the runtime directory",
    )
    parser.add_argument(
        "--add-file-name-comment",
        "--afnc",
        metavar="COMMENT_TOKEN",
        help="prefixes the file contents with a comment containing the original file name",
        type=str,
        action="store",
    )
    parser.add_argument(
        "drop_in_dir",
        help="path of the config drop-in directory where files will be read from",
        type=Path,
    )
    parser.add_argument(
        "runtime_dir",
        help="path of the volatile runtime directory where config will be written to",
        type=Path,
    )
    parser.add_argument(
        "output_file",
        help="name of the file with the content of all drop-in directory files",
        type=Path,
    )
    args = parser.parse_args()

    di_conf = DropInConfiguration(
        args.drop_in_dir,
        args.runtime_dir,
        args.output_file,
        args.add_file_name_comment,
    )
    di_conf.write_runtime_config_file()
