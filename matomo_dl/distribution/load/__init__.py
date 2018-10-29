import pathlib
import typing as typ

from matomo_dl.distribution.file import DistributionFile
from matomo_dl.distribution.lock import DistributionLockFile
from .file import load_distribution_file


def lockfile_path_from_distribution(distribution_file: pathlib.Path) -> pathlib.Path:
    distribution_lock_file = distribution_file.with_suffix(
        ".lock" + distribution_file.suffix
    )
    return distribution_lock_file


def load_from_distribution_path(
    distribution_file: pathlib.Path
) -> typ.Tuple[DistributionFile, typ.Optional[DistributionLockFile]]:
    # distribution_lockfile = lockfile_path_from_distribution(distribution_file)

    dist = load_distribution_file(
        distribution_file.parent, distribution_file.read_text()
    )
    lock = None
    return dist, lock
