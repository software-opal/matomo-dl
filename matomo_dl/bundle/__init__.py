import logging
import pathlib
import tarfile
import tempfile
import typing as typ
import gzip
from contextlib import ExitStack

import toml

from matomo_dl.distribution.file import DistributionFile
from matomo_dl.distribution.lock import DistributionLockFile
from matomo_dl.errors import DownloadHashMismatch
from matomo_dl.lock.matomo import get_cache_key
from matomo_dl.session import SessionStore
from matomo_dl.progress import progressbar
from .customisation import apply_customisations
from .extract import extract_zip_file
from .info import BuildInformation
from .plugin import extract_plugins
from .stat import standardise_mode

logger = logging.getLogger(__name__)


def build_release(
    session: SessionStore,
    dist: DistributionFile,
    lock: DistributionLockFile,
    output_file: pathlib.Path,
):
    with tempfile.TemporaryDirectory(prefix="matomo-dl") as f:
        folder = pathlib.Path(f)
        info = BuildInformation(lock, dist.customisation, folder)
        extract_matomo(session, info)
        extract_plugins(session, dist.license_key, info)

        apply_customisations(info)

        (folder / ".build.toml").write_text(toml.dumps(info.to_output()))
        create_release_tarball(info, output_file)


def extract_matomo(session: SessionStore, build: BuildInformation):
    lock = build.lockfile.matomo
    folder = build.folder
    data = session.retrieve_cache_data(get_cache_key(lock.version), lock.hash)
    if not data:
        r = session.get(lock.link)
        data = r.content
        data_hash = session.store_cache_data(get_cache_key(lock.version), data)
        if lock.hash != data_hash:
            raise DownloadHashMismatch()
    latest_mtime = extract_zip_file(
        data, folder, root=lock.extraction_root, progress="Extracting Matomo"
    )
    assert latest_mtime is not None
    build.add_source_time(latest_mtime)


def create_release_tarball(build: BuildInformation, output_file: pathlib.Path):
    if output_file.suffixes[0] != ".tar":
        output_file = output_file.with_suffix(".tar.gz")
    with ExitStack() as stack:
        bar = stack.enter_context(progressbar(length=3, label="Creating archive"))
        if output_file.suffix == ".tar":
            file = stack.enter_context(tarfile.open(output_file, mode="w"))
        elif output_file.suffix == ".gz":
            output_fd = gzip.GzipFile(
                filename="",
                mode="wb",
                compresslevel=9,
                mtime=build.mtime_clamp,
                fileobj=stack.enter_context(output_file.open("wb")),
            )
            file = stack.enter_context(
                tarfile.open(fileobj=stack.enter_context(output_fd), mode="w")
            )
        else:
            if output_file.suffix in [".gz", ".xz"]:
                mode = "w:" + output_file.suffix[1:]
            elif output_file.suffix in [".bz", ".bz2"]:
                mode = "w:bz2"
            else:
                raise ValueError()
            file = stack.enter_context(
                tarfile.open(output_file, mode=mode, compresslevel=9)
            )
        bar.update(1)
        items = list(iter_folder_for_tar(file, build, build.folder, ""))
        bar.update(2)
        bar = stack.enter_context(progressbar(items, label="Creating archive"))
        for tar_info, path in bar:
            if path:
                with path.open("rb") as f:
                    file.addfile(tar_info, f)
            else:
                file.addfile(tar_info)


def normalise_tar_info(
    build: BuildInformation, info: tarfile.TarInfo
) -> typ.Optional[tarfile.TarInfo]:
    if not info.isfile() and not info.isdir():
        return None
    if info.mode & 0o7000 != 0:
        print(info, info.mode)
        raise ValueError()
    info.mode = standardise_mode(info.mode, force_exec=info.isdir())
    info.uid = 0
    info.uname = ""
    info.gid = 0
    info.gname = ""
    info.pax_headers = {}
    # Clamp any files modified during this run to the start;
    # See https://reproducible-builds.org/docs/source-date-epoch/
    info.mtime = build.clamp_mtime(info.mtime)
    return info


def iter_folder_for_tar(
    tar: tarfile.TarFile, build: BuildInformation, folder: pathlib.Path, base_path: str
):
    if base_path != "" and base_path[-1] != "/":
        base_path += "/"
    for path in sorted(folder.iterdir()):
        tar_info = normalise_tar_info(
            build, tar.gettarinfo(str(path), f"{base_path}{path.name}")
        )
        if not tar_info:
            continue
        elif tar_info.isfile():
            yield tar_info, path
        elif tar_info.isdir():
            yield tar_info, None
            yield from iter_folder_for_tar(tar, build, path, f"{base_path}{path.name}/")
