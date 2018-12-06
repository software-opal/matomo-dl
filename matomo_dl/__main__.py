import logging
import pathlib

import click
import click_log

from matomo_dl import __version__
from matomo_dl.bundle import build_release
from matomo_dl.distribution.load_save import (
    diff_lockfiles,
    load_from_distribution_path,
    write_lockfile_using_distribution_path,
)
from matomo_dl.errors import MatomoError
from matomo_dl.lock.general import build_lock
from matomo_dl.session import (
    CACHE_LEVEL_NAMES,
    DEFAULT_CACHE_LEVEL,
    SessionStore,
    create_session,
)

logger = logging.getLogger(__name__)
click_log.basic_config()
cache_level_choices = sorted(
    set(
        tuple(map(str, CACHE_LEVEL_NAMES.keys()))
        + tuple(map(str, CACHE_LEVEL_NAMES.values()))
    )
)


@click.group()
@click.version_option(version=__version__)
@click_log.simple_verbosity_option(logger)
@click.option(
    "--cache",
    "--cache-dir",
    "-C",
    "cache_dir",
    type=click.Path(exists=False, file_okay=False),
    show_envvar=True,
)
@click.option(
    "--cache-level",
    "cache_level",
    default=str(DEFAULT_CACHE_LEVEL),
    type=click.Choice(cache_level_choices),
    show_envvar=True,
)
@click.option("--clear", "cache_clear", is_flag=True, default=False)
@click.pass_context
def cli(ctx, cache_dir: str, cache_level: str, cache_clear: bool):
    ctx.ensure_object(dict)

    ctx.obj["session"] = create_session(
        cache_dir=cache_dir, level=cache_level, clear=cache_clear
    )
    pass


@cli.command()
@click.option("--diff/--no-diff", "-d/ ", "diff", default=True)
@click.option("--dry", "dry", default=False, is_flag=True)
@click.argument(
    "distribution_file",
    default="./distribution.toml",
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
)
@click.pass_context
def update(ctx, distribution_file, dry, diff):
    session = ctx.obj["session"]
    assert isinstance(session, SessionStore)
    distribution_file = pathlib.Path(distribution_file)
    dist, lock = load_from_distribution_path(distribution_file)
    try:
        new_lock = build_lock(session, dist, lock)
    except MatomoError as e:
        click.echo(
            "🛑 "
            + click.style("Error: ", fg="red", bold=True)
            + click.style(str(e), fg="red")
            + " 🛑"
        )
        return ctx.exit(2)
    if new_lock != lock:
        if diff:
            diff_lockfiles(lock, new_lock)
        if dry:
            click.secho("! File has changes !")
            if not diff:
                click.secho("Run with '--diff' to see the changes")
        else:
            write_lockfile_using_distribution_path(distribution_file, new_lock)
            click.secho("✨ Written lock file changes ✨", fg="green", bold=True)
    else:
        click.secho("✨ Already up to date ✨", fg="green")


@cli.command()
@click.option(
    "--fail-if-updates/--no-fail-if-updates", "-f/ ", "fail_if_updates", default=False
)
@click.option(
    "--update/--no-update", "--sync/ ", "-u/-U", "update_locks", default=False
)
@click.option(
    "--output",
    "-o",
    "output_file",
    default="./matomo.tar.gz",
    type=click.Path(exists=False, resolve_path=True, dir_okay=False),
)
@click.argument(
    "distribution_file",
    default="./distribution.toml",
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
)
@click.pass_context
def build(ctx, distribution_file, output_file, update_locks, fail_if_updates):
    update_kws = {}
    if update_locks is True:
        update_kws["diff"] = True
        update_kws["dry"] = False
    if fail_if_updates is True:
        update_kws["diff"] = True
        update_kws["dry"] = True
    if update_kws:
        click.secho("🔄 Checking for updates before building 🔄")
        ctx.invoke(update, distribution_file=distribution_file, **update_kws)

    click.secho("  Building your distribution  ")
    session = ctx.obj["session"]
    assert isinstance(session, SessionStore)
    distribution_file = pathlib.Path(distribution_file)
    dist, lock = load_from_distribution_path(distribution_file)
    if not lock:
        click.secho(
            "⛔ The distribution file hasn't been locked ⛔", fg="yellow", bold=True
        )
        click.echo("Add '--sync' to create one as part of the build.")
        ctx.exit(1)
    if lock.distribution_hash != dist.versioning_hash:
        click.secho("⛔ The distribution file has changed ⛔", fg="yellow", bold=True)
        click.echo("Cowardly refusing to build from an outdated lock file.")
        click.echo("Add '--sync' to perform an update.")
        ctx.exit(1)
    try:
        build_release(session, dist, lock, pathlib.Path(output_file))
        click.secho("🎉 Built your distribution 🎉", fg="green")
    except MatomoError as e:
        click.echo(
            "💥 "
            + click.style("Error: ", fg="red", bold=True)
            + click.style(str(e), fg="red")
            + " 💥"
        )
        return ctx.exit(2)


if __name__ == "__main__":
    cli(
        auto_envvar_prefix="MATOMO_DL",
        token_normalize_func=lambda s: str(s).strip().lower(),
    )
