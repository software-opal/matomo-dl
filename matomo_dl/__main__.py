import pathlib

import click

from .distribution.load import load_from_distribution_path
from .distribution.lock import DistributionLockFile
from .lock.matomo import sync_matomo_lock
from .lock.plugin import sync_plugin_lock
from .session import SessionStore


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--cache",
    "--cache-dir",
    "-C",
    "cache_dir",
    envvar="MATOMO_DL_CACHE_DIR",
    type=click.Path(exists=False, file_okay=False),
)
@click.argument(
    "distribution_file",
    default="./distribution.toml",
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
)
def update(distribution_file, cache_dir):
    if cache_dir:
        cache_dir = pathlib.Path(cache_dir)
        cache_dir.resolve(strict=False)
        cache_dir.mkdir(parents=True, exist_ok=True)
    else:
        cache_dir = None
    distribution_file = pathlib.Path(distribution_file)
    dist, lock = load_from_distribution_path(distribution_file)
    session = SessionStore(cache_dir=cache_dir)

    matomo_lock = sync_matomo_lock(session, dist.version, lock.matomo if lock else None)
    if lock:
        old_plugin_locks = {name.lower(): lock for name, lock in lock.plugins.items()}
    else:
        old_plugin_locks = {}
    license_key = lock.license_key if lock else None
    plugin_locks = {}
    for plugin in dist.plugins:
        p_lock = sync_plugin_lock(
            session, license_key, plugin, old_plugin_locks.get(plugin.name.lower())
        )
        plugin_locks[plugin.name.lower()] = p_lock

    new_lock = DistributionLockFile(matomo=matomo_lock)


@cli.command()
def build():
    click.echo("Dropped the database")


if __name__ == "__main__":
    cli()
