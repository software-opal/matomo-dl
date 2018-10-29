import typing as typ

import attr

from matomo_dl.hashing import HashInfo
from .version import ExactVersion


@attr.s
class MatomoLock:

    version: ExactVersion = attr.ib()
    link: str = attr.ib()
    hashes: HashInfo = attr.ib()
    extraction_root: str = attr.ib()


@attr.s
class PluginLock:

    extraction_root: str = attr.ib()


@attr.s
class VersionedPluginLock(PluginLock):

    version: ExactVersion = attr.ib()
    link: str = attr.ib()
    hashes: HashInfo = attr.ib()


@attr.s
class GitPluginLock(PluginLock):

    git: str = attr.ib()
    ref: str = attr.ib()
    hashes: HashInfo = attr.ib()


@attr.s
class RawPluginLock(PluginLock):

    link: str = attr.ib()
    hashes: HashInfo = attr.ib()


@attr.s
class DistributionLockFile:

    matomo: MatomoLock = attr.ib()
    plugin_locks: typ.Mapping[str, PluginLock] = attr.ib()
