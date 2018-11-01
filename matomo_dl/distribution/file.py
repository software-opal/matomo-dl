import json
import os
import pathlib
import typing as typ
from hashlib import sha256

import attr
import cattr
import toml

from .customisations import Customisations
from .version import AnyVersion, Version


class Plugin:
    pass


@attr.s
class VersionedPlugin(Plugin):

    version: Version = attr.ib()


@attr.s
class GitPlugin(Plugin):

    git: str = attr.ib()
    ref: typ.Optional[str] = attr.ib()


@attr.s
class RawPlugin(Plugin):

    link: str = attr.ib()


@attr.s
class DistributionFile:

    version: Version = attr.ib()
    php_version: typ.Optional[str] = attr.ib(default=None)
    license_key: typ.Optional[str] = attr.ib(default=None)
    plugins: typ.Mapping[str, Plugin] = attr.ib(factory=dict)
    customisation: Customisations = attr.ib(factory=Customisations)

    @classmethod
    def _normalise_license_key(
        cls, base_dir: typ.Optional[pathlib.Path], key: typ.Optional[str]
    ) -> typ.Optional[str]:
        if key is None:
            return None
        key = key.strip()
        if not key:
            return None
        elif key[0] == "$":
            return cls._normalise_license_key(base_dir, os.environ[key[1:]])
        elif key[0] == "<":
            if base_dir is None:
                raise ValueError("Cannot normalise a file include without a base path")
            return cls._normalise_license_key(
                base_dir, (base_dir / key[1:]).read_text()
            )
        else:
            return key

    def normalise_license_key(self, base_dir: typ.Optional[pathlib.Path]):
        self.license_key = self._normalise_license_key(base_dir, self.license_key)

    @property
    def versioning_hash(self) -> str:
        versioning_json = json.dumps(
            {
                "version": cattr.unstructure(self.version),
                "php_version": cattr.unstructure(self.php_version),
                "plugins": cattr.unstructure(self.plugins),
            },
            indent=None,
            separators=(",", ":"),
            sort_keys=True,
        )
        return "sha256:" + sha256(versioning_json.encode("utf-8")).hexdigest()


def parse_plugin(value, _typ) -> Plugin:
    if value is None:
        return VersionedPlugin(AnyVersion())
    elif isinstance(value, str):
        return VersionedPlugin(cattr.structure(value, Version))
    elif not isinstance(value, dict):
        raise ValueError("Unsupported plugin type {value!r}")
    elif "version" in value:
        value = value.pop("version")
        if value is None:
            return VersionedPlugin(AnyVersion())
        elif isinstance(value, str):
            return VersionedPlugin(cattr.structure(value, Version))
    elif "git" in value:
        return GitPlugin(**value)
    elif "link" in value:
        return RawPlugin(**value)
    raise ValueError("Unsupported plugin type {value!r}")


cattr.register_structure_hook(Plugin, parse_plugin)


def unstringify_distribution_file(
    base_dir: pathlib.Path, file_content: str
) -> DistributionFile:
    v: DistributionFile = cattr.structure(toml.loads(file_content), DistributionFile)
    v.normalise_license_key(base_dir)
    return v


def stringify_distribution_file(dist_file: DistributionFile) -> str:
    return toml.dumps(cattr.unstructure(dist_file))
