import pathlib
import typing as typ

import attr

from ..hashing import HashInfo
from .version import ExactVersion


@attr.s
class MatomoLock:

    version: ExactVersion = attr.ib()
    link: str = attr.ib()
    hashe: HashInfo = attr.ib()
    extraction_root: str = attr.ib()


@attr.s
class LicenseLock:
    hash: HashInfo = attr.ib()


@attr.s
class PluginLock:

    extraction_root: str = attr.ib()


@attr.s
class VersionedPluginLock(PluginLock):

    version: ExactVersion = attr.ib()
    link: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class GitPluginLock(PluginLock):

    git: str = attr.ib()
    ref: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class RawPluginLock(PluginLock):

    link: str = attr.ib()
    hash: HashInfo = attr.ib()


@attr.s
class DistributionLockFile:

    matomo: MatomoLock = attr.ib()
    license_key: typ.Optional[LicenseLock] = attr.ib()
    plugin_locks: typ.Mapping[str, PluginLock] = attr.ib()
