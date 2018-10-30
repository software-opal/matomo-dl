import typing as typ

import attr
import cattr
from packaging.specifiers import SpecifierSet


class Version:

    version: typ.Optional[str] = None
    specifier: SpecifierSet

    @property
    def matches_one_only(self) -> bool:
        return isinstance(self, ExactVersion)

    @property
    def matches_any(self) -> bool:
        return isinstance(self, AnyVersion)

    def choose_version(self, versions: typ.Collection[str]) -> typ.Optional[str]:
        if self.matches_one_only:
            return self.version if self.version in versions else None
        if not versions:
            return None
        assert isinstance(self.specifier, SpecifierSet), repr(self) + repr(
            self.specifier
        )
        matching: typ.List[str] = sorted(self.specifier.filter(versions))
        if not matching:
            return None
        else:
            return matching[-1]

    def __str__(self) -> str:
        return str(self.specifier)


@attr.s
class AnyVersion(Version):
    @property
    def specifier(self) -> SpecifierSet:
        return SpecifierSet("")

    def __str__(self) -> str:
        return "*"


@attr.s
class DynamicVersion(Version):

    specifier: SpecifierSet = attr.ib()


@attr.s
class ExactVersion(Version):

    matches_one_only = True
    version: str = attr.ib()

    @property
    def specifier(self) -> SpecifierSet:
        return SpecifierSet(f"=={self.version}")

    def __str__(self) -> str:
        return self.version


def parse_version(version: str) -> Version:
    version = version.strip()
    if version == "*":
        return AnyVersion()
    if "," in version or version[0] in ["<", ">", "=", "~", "!"]:
        spec_set = SpecifierSet(version)
    else:
        spec_set = SpecifierSet("==" + version)
    if len(spec_set) == 1:
        spec = next(iter(spec_set))
        if spec.operator == "==" and not spec.version.endswith(".*"):
            # Equal, and not a '*' thing. Must be exact.
            return ExactVersion(spec.version)
    return DynamicVersion(spec_set)


def cattr_parse_version(value, _typ) -> Version:
    return parse_version(str(value))


cattr.register_structure_hook(Version, cattr_parse_version)
cattr.register_structure_hook(AnyVersion, cattr_parse_version)
cattr.register_structure_hook(DynamicVersion, cattr_parse_version)
cattr.register_structure_hook(ExactVersion, cattr_parse_version)

cattr.register_unstructure_hook(Version, str)
cattr.register_unstructure_hook(AnyVersion, str)
cattr.register_unstructure_hook(DynamicVersion, str)
cattr.register_unstructure_hook(ExactVersion, str)
