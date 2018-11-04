import logging
import os
import pathlib
import time
import typing as typ

import attr
import cattr

from matomo_dl.distribution.lock import DistributionLockFile

logger = logging.getLogger(__name__)
BUILD_START_TIME = round(time.time())


def get_environ_build_mtime() -> typ.Optional[int]:
    if os.environ.get("SOURCE_DATE_EPOCH", None):
        try:
            return int(os.environ["SOURCE_DATE_EPOCH"])
        except ValueError:
            raise ValueError(
                "The value in $SOURCE_DATE_EPOCH is not a parsable integer"
            )
    return None


def get_build_mtime(default: typ.Optional[int] = None) -> int:
    env_mtime = get_environ_build_mtime()
    if env_mtime is None:
        if default is None:
            return BUILD_START_TIME
        else:
            return default
    else:
        return env_mtime


@attr.s
class BuildInformation:

    lockfile: DistributionLockFile = attr.ib()
    customisations: "Customisations" = attr.ib()
    folder: pathlib.Path = attr.ib()
    extra_info: typ.Dict[str, typ.Any] = attr.ib(factory=dict)
    mtime_clamp: int = attr.ib(factory=get_build_mtime)

    def add_source_time(self, source: int):
        if source > BUILD_START_TIME:
            logger.warning("Source built after build started.")
        elif self.mtime_clamp == BUILD_START_TIME:
            self.mtime_clamp = source
        else:
            self.mtime_clamp = max(self.mtime_clamp, source + 1)

    def clamp_mtime(self, source: typ.Union[int, float]) -> int:
        return int(min(source, self.mtime_clamp))

    def to_output(self) -> typ.Dict[str, typ.Any]:
        data: typ.Dict[str, typ.Any] = cattr.unstructure(self)
        del data["folder"]
        return data

    def add_removed_files(self, files: typ.Iterable[typ.Union[pathlib.Path, str]]):
        clean_files: typ.Set[str] = set()
        if "removed_files" in self.extra_info:
            clean_files.update(self.extra_info["removed_files"])
        for file in files:
            if isinstance(file, pathlib.Path):
                if file.is_absolute():
                    clean_files.add(str(file.relative_to(self.folder)))
                else:
                    clean_files.add(str(file))
            else:
                clean_files.add(str(file))
        self.extra_info["removed_files"] = sorted(clean_files)


if typ.TYPE_CHECKING:
    # At the end to avoid a recursive import
    from matomo_dl.distribution.customisations import Customisations
else:
    Customisations = None
