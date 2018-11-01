import typing as typ

import attr

from matomo_dl.bundle.customisation import CustomisationCollection
from matomo_dl.bundle.customisation.manifest import regenerate_manifest
from matomo_dl.call_tree import OrderedCall

oc_from_c = OrderedCall.from_callable


def filter_customisations(
    *fns: typ.Tuple[bool, OrderedCall]
) -> CustomisationCollection:
    out_fns = []
    for include, fn in fns:
        if include:
            out_fns.append(fn)
    return out_fns


class Customisation:
    def get_customisation_functions(self) -> CustomisationCollection:
        raise NotImplementedError()


@attr.s
class ManifestCustomisation(Customisation):

    regenerate: bool = attr.ib(default=True)

    def get_customisation_functions(self) -> CustomisationCollection:
        return filter_customisations(
            (self.regenerate, oc_from_c(regenerate_manifest, requires=["ALL"]))
        )


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

    def get_customisation_functions(self) -> CustomisationCollection:
        return filter_customisations(
            # (self.documentation, oc_from_c(remove_documentation, affects=["FILES"])),
            # (self.build_support, oc_from_c(remove_build_support, affects=["FILES"])),
            # (self.tests, oc_from_c(remove_tests, affects=["FILES"])),
            # (self.git_support, oc_from_c(remove_git_support, affects=["FILES"])),
            # (
            #     self.example_plugins,
            #     oc_from_c(remove_example_plugins, affects=["FILES", "PLUGINS"]),
            # ),
            # (
            #     self.vendored_extras,
            #     oc_from_c(remove_vendored_extras, affects=["FILES"]),
            # ),
            # (
            #     self.marketplace,
            #     oc_from_c(remove_marketplace, affects=["FILES", "PLUGINS"]),
            # ),
            # (
            #     self.professional_services,
            #     oc_from_c(remove_professional_services, affects=["FILES", "PLUGINS"]),
            # ),
        )


@attr.s
class UpdateCustomisation(Customisation):

    cacert: bool = attr.ib()

    def get_customisation_functions(self) -> CustomisationCollection:
        return filter_customisations()


@attr.s
class ConfigPlugins:

    delete_examples: bool = attr.ib()
    add_installed: bool = attr.ib()

    def get_customisation_functions(self) -> CustomisationCollection:
        return filter_customisations()


@attr.s
class ConfigPluginsInstalled:

    delete_examples: typ.Optional[bool] = attr.ib()
    add_installed: typ.Optional[bool] = attr.ib()
    delete_marketplace: typ.Optional[bool] = attr.ib()
    delete_professional_services: typ.Optional[bool] = attr.ib()

    def get_customisation_functions(self) -> CustomisationCollection:
        return filter_customisations()


@attr.s
class Customisations(Customisation):
    manifest: typ.Optional[ManifestCustomisation] = attr.ib(default=None)
    remove: typ.Optional[RemoveCustomisation] = attr.ib(default=None)
    update: typ.Optional[UpdateCustomisation] = attr.ib(default=None)

    def get_customisation_functions(self) -> CustomisationCollection:
        fns: typ.List[OrderedCall] = []
        if self.manifest is not None:
            fns.extend(self.manifest.get_customisation_functions())
        if self.remove is not None:
            fns.extend(self.remove.get_customisation_functions())
        if self.update is not None:
            fns.extend(self.update.get_customisation_functions())
        return fns
