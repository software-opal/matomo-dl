import logging
import typing as typ
from urllib.parse import urljoin

import requests

from matomo_dl.distribution.lock import VersionedPluginLock
from matomo_dl.distribution.version import Version, parse_version
from matomo_dl.errors import VersionError
from matomo_dl.lock import get_zip_extraction_root
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)
PLUGIN_API_URL = "https://plugins.matomo.org"


def sync_versioned_plugin_lock(
    session: SessionStore,
    php_version: str,
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

    cache_key = f"plugin-{name}-{version}-zip"
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
    php_version: str,
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


def get_all_plugin_versions(
    session: requests.Session,
    php_version: typ.Optional[str],
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
) -> typ.Tuple[typ.Optional[str], typ.Mapping[str, str]]:
    resp = plugin_request(
        session,
        f"{PLUGIN_API_URL}/api/2.0/plugins/{name}/info?coreVersion={matomo_version}",
        license_key=license_key,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("isDownloadable", False):
        logger.warning(f"Cannot download {name!r} with current configuration.")
        if data["isPaid"]:
            if license_key:
                logger.warning(
                    f"The license key given('{license_key[:5]}...') is cannot "
                    f"download the paid plugin {name!r}."
                )
            else:
                logger.warning(
                    f"You must specify a license key to download the paid plugin {name!r}."
                )
        return (None, {})
    latest_version = data.get("latestVersion", None)
    all_versions = {}
    filtered_versions = {}
    for version_data in data.get("versions", []):
        version = version_data.get("name")
        dl_url = urljoin(resp.url, version_data.get("download"))
        all_versions[version] = dl_url
        if "piwik" in version_data.get("requires", {}):
            matomo = parse_version(version_data["requires"]["piwik"])
            if not matomo.choose_version([matomo_version]):
                continue
        if php_version and "php" in version_data.get("requires", {}):
            php = parse_version(version_data["requires"]["php"])
            if not php.choose_version([php_version]):
                continue
        filtered_versions[version] = dl_url
    if not filtered_versions:
        logger.warning(
            f"There are no versions of {name!r} supported on"
            f" Matomo {matomo_version} and PHP {php_version}."
        )
        return (None, {})
    if latest_version not in all_versions:
        # A very bizar occurance
        return None, filtered_versions
    elif latest_version not in filtered_versions:
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
    if "data" in k and isinstance(k["data"], typ.MutableMapping):
        k["data"].setdefault("access_token", license_key)
    resp = session.post(*a, **k)
    if resp.status_code in [401, 403]:
        logger.warning("License key denied. Contact Matomo for support.")
        if "data" in k and isinstance(k["data"], typ.MutableMapping):
            k["data"].pop("access_token", None)
        return plugin_request(*a, **k, data=data)
    return resp
