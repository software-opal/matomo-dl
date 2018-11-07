import pathlib
import typing as typ

import click

from matomo_dl.colored_diff import ColoredDiffer
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


def diff_lockfiles(
    old: typ.Optional[DistributionLockFile], new: DistributionLockFile, quieter=False
):
    if old == new:
        if not quieter:
            click.secho("No changes")
        return
    if old is None:
        old_txt = ""
    else:
        old_txt = stringify_distribution_lock(old)
    new_txt = stringify_distribution_lock(new)
    # We should have a diff at this point; if old != new and old_txt == new_txt then we have a bug
    assert old_txt != new_txt
    if old and old.distribution_hash != new.distribution_hash:
        if not quieter:
            click.secho(
                "# Note: these files were built from different distribution configurations",
                dim=True,
            )
    click.secho("--- Old")
    click.secho("+++ New")
    for line in ColoredDiffer().compare(old_txt, new_txt):
        click.echo(line)
