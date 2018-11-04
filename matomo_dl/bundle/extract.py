import logging
import os
import pathlib
import typing as typ
import zipfile
from contextlib import ExitStack
from datetime import datetime
from io import BytesIO

from matomo_dl.progress import progressbar
from .stat import is_extended_mode_dir, standardise_privacy_mode

logger = logging.getLogger(__name__)


def is_zipinfo_dir(info: zipfile.ZipInfo) -> bool:
    is_msdos_dir = bool(info.external_attr & 0x10)
    is_unix_dir = bool(is_extended_mode_dir(info.external_attr >> 16))
    return is_msdos_dir or is_unix_dir or info.filename[-1] == "/"


def resolve_filename(
    destination: pathlib.Path, name: str
) -> typ.Optional[pathlib.Path]:
    target = (destination / name).resolve(strict=False)
    if (
        len(target.parts) <= len(destination.parts)
        or target.parts[: len(destination.parts)] != destination.parts
    ):
        return None
    return target


def extract_zip_file(
    file_data: bytes,
    destination: pathlib.Path,
    root: str,
    progress: typ.Optional[str] = None,
) -> typ.Optional[int]:
    latest_mtime = None
    with ExitStack() as stack:
        file = stack.enter_context(zipfile.ZipFile(BytesIO(file_data), "r"))
        infos: typ.Iterable[zipfile.ZipInfo] = file.infolist()
        if progress:
            infos = stack.enter_context(progressbar(infos, label=progress))
        for item in infos:
            _, root_chk, dest_filename = item.filename.partition(root)
            if root_chk != root:
                continue
            elif not dest_filename:
                destination.mkdir(parents=True, exist_ok=True)
                continue
            dest = resolve_filename(destination, dest_filename)
            if not dest:
                logger.warning(
                    f"Skipping potentially dangeous item {item.filename!r}, "
                    f"it was to be placed at {dest_filename!r}"
                )
                continue
            if is_zipinfo_dir(item):
                dest.mkdir(parents=True, exist_ok=True)
            else:
                mtime = int(datetime(*item.date_time, microsecond=0).timestamp())
                if latest_mtime is None:
                    latest_mtime = mtime
                else:
                    latest_mtime = max(latest_mtime, mtime)
                # File
                mode = standardise_privacy_mode(item.external_attr >> 16)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(file.read(item))
                dest.chmod(mode)
                os.utime(dest, times=(mtime, mtime))
    return latest_mtime
