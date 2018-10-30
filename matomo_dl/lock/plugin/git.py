import logging
import subprocess
import tempfile
import typing as typ
from contextlib import ExitStack
from hashlib import sha256

from matomo_dl.distribution.lock import GitPluginLock
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)


def sync_git_plugin_lock(
    session: SessionStore,
    php_version: str,
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
    git_url: str,
    ref: typ.Optional[str],
    existing_lock: typ.Optional[GitPluginLock],
) -> GitPluginLock:
    if not ref:
        ref = "master"
    if existing_lock and ref and existing_lock.sha == ref:
        # Specifying an exact sha & we already locked it.
        return existing_lock
    sha, archive = get_plugin_using_archive(git_url, ref)
    if not sha:
        # Ref may be missing; or the remote server isn't letting us archive a commit sha.
        sha, archive = get_plugin_using_clone(git_url, ref)
    if sha:
        archive_hash = session.store_cache_data(
            f"git-plugin-{name}-{archive_sha}-tar", archive
        )
        return GitPluginLock(git=git_url, sha=archive_sha, hash=archive_hash)
    else:
        logger.warning("Cannot retrieve {ref!r} fron {git_url!r}.")
        raise MatomoError("Cannot create an archive of {ref!r}. Does it exist?")


def get_plugin_using_archive(
    git_url: str, ref: str
) -> typ.Tuple[typ.Optional[str], typ.Optional[bytes]]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".tar", mode="rb") as tarball:
            archive_res = subprocess.run(
                [
                    "git",
                    "archive",
                    "--format=tar",
                    "--output",
                    tarball.name,
                    "--remote",
                    git_url,
                    ref,
                ],
                check=True,
            )
            with open(tarball.name, "rb") as f:
                # Prefer 'stdin' over 'input' as this command only uses the first part of the file
                res = subprocess.run(
                    ["git", "get-tar-commit-id"],
                    stdin=f,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    check=True,
                )
            return res.stdout.strip(), tarball.read()
    except subprocess.CalledProcessError:
        return None, None


def get_plugin_using_clone(
    git_url: str, ref: str
) -> typ.Tuple[typ.Optional[str], typ.Optional[bytes]]:
    try:
        with tempfile.TemporaryDirectory() as gitdir:
            subprocess.run(
                ["git", "clone", "--depth=5", "--bare", git_url, gitdir], check=True
            )
            res = subprocess.run(
                ["git", "rev-parse", f"{ref}^{{commit}}"],
                cwd=gitdir,
                universal_newlines=True,
                stdout=subprocess.PIPE,
            )
            if res.returncode != 0:
                subprocess.run(
                    ["git", "fetch", "--unshallow", "origin"], cwd=gitdir, check=True
                )
                res = subprocess.run(
                    ["git", "rev-parse", f"{ref}^{{commit}}"],
                    cwd=gitdir,
                    universal_newlines=True,
                    check=True,
                    stdout=subprocess.PIPE,
                )
            sha = res.stdout.strip()
            with tempfile.NamedTemporaryFile(suffix=".tar", mode="rb") as tarball:
                archive_res = subprocess.run(
                    [
                        "git",
                        "archive",
                        "--format=tar",
                        "--output",
                        tarball.name,
                        "--remote",
                        sha,
                    ],
                    cwd=gitdir,
                    check=True,
                )
                return sha, tarball.read()

    except subprocess.CalledProcessError:
        return None, None
