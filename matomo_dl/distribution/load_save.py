import pathlib
import typing as typ

from matomo_dl.distribution.file import DistributionFile
from matomo_dl.distribution.lock import DistributionLockFile
from .file import stringify_distribution_file, unstringify_distribution_file
from .lock import stringify_distribution_lock, unstringify_distribution_lock


def lockfile_path_from_distribution(distribution_file: pathlib.Path) -> pathlib.Path:
    distribution_lock_file = distribution_file.with_suffix(
        ".lock" + distribution_file.suffix
    )
    return distribution_lock_file


def normfile_path_from_distribution(distribution_file: pathlib.Path) -> pathlib.Path:
    distribution_lock_file = distribution_file.with_suffix(
        ".norm" + distribution_file.suffix
    )
    return distribution_lock_file


def load_from_distribution_path(
    distribution_file: pathlib.Path
) -> typ.Tuple[DistributionFile, typ.Optional[DistributionLockFile]]:
    distribution_lockfile = lockfile_path_from_distribution(distribution_file)

    dist = unstringify_distribution_file(
        distribution_file.parent, distribution_file.read_text()
    )
    normfile_path_from_distribution(distribution_file).write_text(
        stringify_distribution_file(dist)
    )
    try:
        lock = unstringify_distribution_lock(distribution_lockfile.read_text())
    except Exception:
        lock = None
    return dist, lock


def write_lockfile_using_distribution_path(
    distribution_file: pathlib.Path, locks: DistributionLockFile
):
    distribution_lockfile = lockfile_path_from_distribution(distribution_file)
    distribution_lockfile.write_text(stringify_distribution_lock(locks))
