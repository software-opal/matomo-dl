import json
import os
import pathlib
import typing as typ
from hashlib import sha256

import attr
import cattr
import toml
from typing import NewType

from .version import AnyVersion, Version, parse_version


class Plugin:

    name: str

    @staticmethod
    def to_normalised_name(name: str) -> str:
        return name.strip().lower()

    @property
    def normalised_name(self) -> str:
        return self.to_normalised_name(self.name)


@attr.s
class VersionedPlugin(Plugin):

    name: str = attr.ib()
    version: Version = attr.ib()


@attr.s
class GitPlugin(Plugin):

    name: str = attr.ib()
    git: str = attr.ib()
    rev: typ.Optional[str] = attr.ib()


@attr.s
class RawPlugin(Plugin):

    name: str = attr.ib()
    link: str = attr.ib()


class Customisation:
    pass


@attr.s
class ManifestCustomisation(Customisation):

    regenerate: bool = attr.ib(default=True)


@attr.s
class RemoveCustomisation(Customisation):

    example_plugins: bool = attr.ib()
    vendored_extras: bool = attr.ib()
    documentation: bool = attr.ib()
    build_support: bool = attr.ib()
    tests: bool = attr.ib()
    git_support: bool = attr.ib()
    marketplace: bool = attr.ib()
    professional_services: bool = attr.ib()


@attr.s
class UpdateCustomisation(Customisation):

    cacert: bool = attr.ib()


@attr.s
class ConfigPlugins:

    delete_examples: bool = attr.ib()
    add_installed: bool = attr.ib()


@attr.s
class ConfigPluginsInstalled:

    delete_examples: typ.Optional[bool] = attr.ib()
    add_installed: typ.Optional[bool] = attr.ib()
    delete_marketplace: typ.Optional[bool] = attr.ib()
    delete_professional_services: typ.Optional[bool] = attr.ib()


LicenseKey = NewType("LicenseKey", str)


@attr.s
class DistributionFile:

    version: Version = attr.ib()
    php_version: typ.Optional[str] = attr.ib()
    license_key: LicenseKey = attr.ib()
    plugins: typ.Collection[Plugin] = attr.ib()
    customisations: typ.Collection[Customisation] = attr.ib()

    @property
    def versioning_hash(self) -> str:
        return (
            "sha256:"
            + sha256(
                json.dumps(
                    {
                        "version": cattr.unstructure(self.version),
                        "php_version": cattr.unstructure(self.php_version),
                        "plugins": cattr.unstructure(self.plugins),
                    },
                    indent=None,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
        )


def parse_license_key(
    base_dir: pathlib.Path, key: typ.Optional[str]
) -> typ.Optional[str]:
    if key is None:
        return None
    key = key.strip()
    if not key:
        return None
    if key[0] == "$":
        return parse_license_key(base_dir, os.environ[key[1:]])
    elif key[0] == "<":
        return (base_dir / key[1:]).read_text().strip()
    else:
        return key


def parse_plugins(
    plugins: typ.Optional[typ.Mapping[str, typ.Any]]
) -> typ.Collection[Plugin]:
    if not plugins:
        return []
    dat: typ.List[Plugin] = []
    for name, value in plugins.items():
        if isinstance(value, str):
            dat.append(VersionedPlugin(name, parse_version(value)))
        elif value.get("git"):
            dat.append(GitPlugin(name, value["git"], value.get("ref")))
        elif value.get("link"):
            dat.append(RawPlugin(name, value["link"]))
        else:
            dat.append(VersionedPlugin(name, AnyVersion()))
    return dat


def parse_customisations(
    customisations: typ.Optional[typ.MutableMapping[str, typ.Any]]
) -> typ.Collection[Customisation]:
    if not customisations:
        customisations = {}
    customisations.setdefault("manifest", {})
    dat: typ.List[Customisation] = []
    for c_type, config in customisations.items():
        if c_type == "manifest":
            dat.append(cattr.structure(config, ManifestCustomisation))
        elif c_type == "remove":
            dat.append(cattr.structure(config, RemoveCustomisation))
        elif c_type == "update":
            dat.append(cattr.structure(config, UpdateCustomisation))
        else:
            raise ValueError(c_type)
    return dat


def load_distribution_file(
    base_dir: pathlib.Path, file_content: str
) -> DistributionFile:
    data = toml.loads(file_content)

    return DistributionFile(
        php_version=data.get("php"),
        version=parse_version(data.get("version", "*")),
        license_key=parse_license_key(base_dir, data.get("license_key")),
        plugins=parse_plugins(data.get("plugins")),
        customisations=parse_customisations(data.get("customisation")),
    )
