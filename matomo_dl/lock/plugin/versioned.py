import logging
import typing as typ
from urllib.parse import urljoin

import attr
import requests

from matomo_dl.distribution.lock import VersionedPluginLock
from matomo_dl.distribution.version import Version, parse_version
from matomo_dl.errors import MissingDownloadError, VersionError
from matomo_dl.lock import get_zip_extraction_root
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)
PLUGIN_API_URL = "https://plugins.matomo.org"


def get_cache_key(name: str, version: str) -> str:
    return f"plugin-{name.lower()}-{version}-zip"


def sync_versioned_plugin_lock(
    session: SessionStore,
    php_version: typ.Optional[str],
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
    version_spec: Version,
    existing_lock: typ.Optional[VersionedPluginLock],
) -> VersionedPluginLock:
    version, dl_url = resolve_plugin_version_spec(
        session, php_version, matomo_version, license_key, version_spec, name
    )
    if existing_lock and version == existing_lock.version:
        return existing_lock

    cache_key = get_cache_key(name, version)
    resp = plugin_request(session, dl_url, license_key=license_key)
    resp.raise_for_status()
    data = resp.content

    base_path = get_zip_extraction_root(data, "plugin.json")
    if not base_path:
        logger.error("Cannot determine how to extract plugin!")
        raise ValueError("Unable to determine path")
    hashes = session.store_cache_data(cache_key, data)
    return VersionedPluginLock(
        version=version, link=dl_url, extraction_root=base_path, hash=hashes
    )


def resolve_plugin_version_spec(
    session: requests.Session,
    php_version: typ.Optional[str],
    matomo_version: str,
    license_key: typ.Optional[str],
    version_spec: Version,
    name: str,
) -> typ.Tuple[str, str]:
    latest, all_versions = get_all_plugin_versions(
        session, php_version, matomo_version, license_key, name
    )
    if not latest and not all_versions:
        logger.error(f"There are no versions of {name} that are supported.")
        raise VersionError(f"No versions returned for {name}")
    elif latest and version_spec.choose_version([latest]):
        return latest, all_versions[latest]
    else:
        version = version_spec.choose_version(set(all_versions))
        if version:
            return version, all_versions[version]
        else:
            logger.error(
                f"There are no versions of {name} that "
                f"match the version specifier {version_spec}."
            )
            raise VersionError(f"No matching versions for {name}")


@attr.s
class PluginData:

    name: str = attr.ib()
    is_downloadable: bool = attr.ib()
    is_paid: bool = attr.ib()
    versions: typ.Collection[typ.Mapping[str, typ.Any]] = attr.ib()
    latest_version: typ.Optional[str] = attr.ib()
    raw_response: requests.Response = attr.ib()

    def assert_downloadable(self) -> None:
        if self.is_downloadable:
            return
        if self.is_paid:
            raise MissingDownloadError(
                f"The plugin {self.name!r} is a paid-for plugin. Ensure a license "
                f"key is provided which has purchased this plugin"
            )
        else:
            raise MissingDownloadError(
                f"Cannot download {self.name!r} with current configuration."
            )

    def iter_versions(
        self,
    ) -> typ.Iterator[typ.Tuple[str, str, typ.Mapping[str, str]]]:
        for version in self.versions:
            ver = version["name"]
            dl_url = urljoin(self.raw_response.url, version["download"])
            requires = version.get("requires", {})
            yield (ver, dl_url, requires)


def get_plugin_data(
    session: requests.Session,
    license_key: typ.Optional[str],
    name: str,
    matomo_version: typ.Optional[str] = None,
) -> PluginData:
    url = f"{PLUGIN_API_URL}/api/2.0/plugins/{name}/info"
    if matomo_version:
        url += f"?coreVersion={matomo_version}"
    resp = plugin_request(session, url, license_key=license_key)
    resp.raise_for_status()
    data = resp.json()
    return PluginData(
        name=data.get("name"),
        is_downloadable=data.get("isDownloadable", False),
        is_paid=data.get("isPaid", False),
        versions=data.get("versions", ()),
        latest_version=data.get("latestVersion", None),
        raw_response=resp,
    )


def get_all_plugin_versions(
    session: requests.Session,
    php_version: typ.Optional[str],
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
) -> typ.Tuple[typ.Optional[str], typ.Mapping[str, str]]:
    data = get_plugin_data(session, license_key, name, matomo_version)
    data.assert_downloadable()
    latest_version = data.latest_version
    filtered_versions = {}
    for name, dl_url, requires in data.iter_versions():
        if "piwik" in requires:
            matomo = parse_version(requires["piwik"])
            if not matomo.choose_version([matomo_version]):
                continue
        if php_version and "php" in requires:
            php = parse_version(requires["php"])
            if not php.choose_version([php_version]):
                continue
        filtered_versions[name] = dl_url
    if not filtered_versions:
        raise VersionError(
            f"There are no versions of {name!r} supported on"
            f" Matomo {matomo_version} and PHP {php_version}."
        )
        return (None, {})
    if latest_version not in filtered_versions:
        logger.warning(
            f"The latest version of {name!r} is not supported on"
            f" Matomo {matomo_version} and PHP {php_version}."
        )
        return None, filtered_versions
    else:
        return latest_version, filtered_versions


def plugin_request(
    session: requests.Session, *a, license_key: typ.Optional[str] = None, **k
) -> requests.Response:
    if not license_key:
        return session.post(*a, **k)
    data = None
    if "data" not in k:
        k["data"] = {"access_token": license_key}
    elif isinstance(k["data"], typ.MutableMapping):
        k["data"].setdefault("access_token", license_key)
    resp = session.post(*a, **k)
    if resp.status_code in [401, 403]:
        logger.warning("License key denied. Contact Matomo for support.")
        if "data" in k and isinstance(k["data"], typ.MutableMapping):
            k["data"].pop("access_token", None)
        return plugin_request(*a, **k, data=data)
    return resp
