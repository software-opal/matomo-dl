import json
import os
import pathlib
import typing as typ

import attr
import cattr


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
class Customisations:
    manifest: typ.Optional[ManifestCustomisation] = attr.ib(default=None)
    remove: typ.Optional[RemoveCustomisation] = attr.ib(default=None)
    update: typ.Optional[UpdateCustomisation] = attr.ib(default=None)
