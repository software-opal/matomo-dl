import typing as typ

import attr
from packaging.specifiers import SpecifierSet


class Version:

    version: typ.Optional[str] = None
    specifier: typ.Optional[SpecifierSet] = None

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
        assert self.specifier
        matching: typ.List[str] = sorted(self.specifier.filter(versions))
        if not matching:
            return None
        else:
            return matching[-1]


@attr.s
class AnyVersion(Version):
    @property
    def specifier(self):
        return SpecifierSet("")


@attr.s
class DynamicVersion(Version):

    specifier: SpecifierSet = attr.ib()


@attr.s
class ExactVersion(Version):

    version: str = attr.ib()
