
import typing as typ

import attr

from .version import Version


class Plugin:
    pass


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


@attr.s
class DistributionFile:

    version: Version = attr.ib()
    license_key: typ.Optional[str] = attr.ib()
    plugins: typ.Collection[Plugin] = attr.ib()
    customisations: typ.Collection[Customisation] = attr.ib()
