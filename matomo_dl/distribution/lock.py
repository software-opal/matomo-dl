import logging
import typing as typ

import attr
import cattr
import toml

from matomo_dl.hashing import HashInfo

logger = logging.getLogger(__name__)


@attr.s
class MatomoLock:

    version: str = attr.ib()
    link: str = attr.ib()
    hash: HashInfo = attr.ib()
    extraction_root: str = attr.ib()


@attr.s
class PluginLock:

    extraction_root: str = attr.ib()


@attr.s
class VersionedPluginLock(PluginLock):

    version: str = attr.ib()
    link: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class GitPluginLock(PluginLock):

    git: str = attr.ib()
    sha: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class RawPluginLock(PluginLock):

    link: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class DistributionLockFile:

    matomo: MatomoLock = attr.ib()
    plugin_locks: typ.Mapping[str, PluginLock] = attr.ib()
    distribution_hash: str = attr.ib()


def unstringify_distribution_lock(dist_lock: str) -> typ.Optional[DistributionLockFile]:
    try:
        data = toml.loads(dist_lock)
        m_lock = cattr.structure(data.pop("matomo"), MatomoLock)
        p_locks = {}
        for plugin_name, lock in data.pop("plugin_locks").items():
            if lock.get("version"):
                p_lock = cattr.structure(lock, VersionedPluginLock)
            elif lock.get("git"):
                p_lock = cattr.structure(lock, GitPluginLock)
            else:
                p_lock = cattr.structure(lock, RawPluginLock)
            p_locks[plugin_name] = p_lock
        data.setdefault("distribution_hash", "")
        return DistributionLockFile(matomo=m_lock, plugin_locks=p_locks, **data)
    except TypeError:
        logger.warning("Failed to load lock file. Discarding contents")
        return None


def stringify_distribution_lock(dist_lock: DistributionLockFile) -> str:
    return toml.dumps(cattr.unstructure(dist_lock))
