import logging
import pathlib
import typing as typ
from collections import defaultdict
from hashlib import md5
from types import SimpleNamespace

from matomo_dl.bundle.fs_util import iter_tree
from matomo_dl.bundle.info import BuildInformation

logger = logging.getLogger(__name__)


def list_duplicates(build: BuildInformation) -> None:
    files_by_size: typ.Dict[int, typ.Set[pathlib.Path]] = defaultdict(set)
    for file in iter_tree(build.folder):
        if file.is_file():
            files_by_size[file.stat().st_size].add(file)
    for size, file_group in files_by_size.items():
        if size == 0 or len(file_group) < 2:
            continue
        files_by_hash: typ.Dict[str, typ.Set[pathlib.Path]] = defaultdict(set)
        for file in file_group:
            files_by_hash[md5(file.read_bytes()).hexdigest()].add(file)
        for matching_files in files_by_hash.values():
            if len(matching_files) < 2:
                continue
            else:
                print(matching_files)


if __name__ == "__main__":
    d = SimpleNamespace()
    d.folder = pathlib.Path(".")
    list_duplicates(d)  # type: ignore
