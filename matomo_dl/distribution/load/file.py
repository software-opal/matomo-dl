import os
import pathlib
import typing as typ

import cattr
import toml
from packaging.specifiers import SpecifierSet

import matomo_dl.distribution.file as dist_file
import matomo_dl.distribution.version as dist_version


def parse_version(version: str) -> dist_file.Version:
    version = version.strip()
    if version == "*":
        return dist_version.AnyVersion()
    if "," in version or version[0] in ["<", ">", "=", "~", "!"]:
        spec_set = SpecifierSet(version)
    else:
        spec_set = SpecifierSet("==" + version)
    if len(spec_set) == 1:
        spec = next(iter(spec_set))
        if spec.operator == "==" and not spec.version.endswith(".*"):
            # Equal, and not a '*' thing. Must be exact.
            return dist_version.ExactVersion(spec.version)
    return dist_version.DynamicVersion(version)


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
) -> typ.Collection[dist_file.Plugin]:
    if not plugins:
        return []
    dat: typ.List[dist_file.Plugin] = []
    for name, value in plugins.items():
        if isinstance(value, str):
            dat.append(dist_file.VersionedPlugin(name, parse_version(value)))
        elif value.get("git"):
            dat.append(
                dist_file.GitPlugin(name, value["git"], value.get("ref") or "master")
            )
        elif value.get("link"):
            dat.append(dist_file.RawPlugin(name, value["link"]))
        else:
            dat.append(dist_file.VersionedPlugin(name, dist_version.AnyVersion()))
    return dat


def parse_customisations(
    customisations: typ.Optional[typ.MutableMapping[str, typ.Any]]
) -> typ.Collection[dist_file.Customisation]:
    if not customisations:
        customisations = {}
    customisations.setdefault("manifest", {})
    dat: typ.List[dist_file.Customisation] = []
    for c_type, config in customisations.items():
        if c_type == "manifest":
            dat.append(dist_file.ManifestCustomisation(**config))
        elif c_type == "remove":
            dat.append(dist_file.RemoveCustomisation(**config))
        elif c_type == "update":
            dat.append(dist_file.UpdateCustomisation(**config))
        else:
            raise ValueError(c_type)
    return dat


def load_distribution_file(
    base_dir: pathlib.Path, file_content: str
) -> dist_file.DistributionFile:
    data = toml.loads(file_content)

    return dist_file.DistributionFile(
        version=parse_version(data.get("version", "*")),
        license_key=parse_license_key(base_dir, data.get("license_key")),
        plugins=parse_plugins(data.get("plugins")),
        customisations=parse_customisations(data.get("customisation")),
    )


def write_distribution_file(dist_file: dist_file.DistributionFile) -> str:
    data = cattr.unstructure(dist_file)
