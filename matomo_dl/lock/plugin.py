import functools
import logging
import re
import typing as typ
import zipfile
from io import BytesIO
from urllib.parse import urljoin

import click
import requests
from packaging.specifiers import SpecifierSet

from matomo_dl.distribution.file import Plugin
from matomo_dl.distribution.lock import PluginLock
from matomo_dl.distribution.version import Version
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)
API_URL = "https://api.matomo.org"


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


def sync_plugin_lock(
    session: SessionStore,
    php_version: str,
    matomo_version: str,
    license_key: typ.Optional[str],
    plugin: Plugin,
    plugin_locks: typ.Optional[PluginLock],
) -> PluginLock:

    pass


def resolve_plugin_version_spec(
    session: requests.Session,
    php_version: str,
    matomo_version: str,
    license_key: typ.Optional[str],
    version_spec: Version,
    name: str,
) -> str:
    if version_spec.version and version_spec.matches_one_only:
        return version_spec.version
    latest, all_versions = get_all_plugin_versions(
        session, php_version, matomo_version, license_key, name
    )
    if not latest and not all_versions:
        logger.error("There are no versions of {name} that are supported.")
        raise ValueError("No supported versions")
    elif latest and version_spec.choose_version([latest]):
        return latest
    else:
        version = version_spec.choose_version(set(all_versions))
        if version:
            return version
        else:
            logger.error(
                "There are no versions of {name} that match the version specifier {version_spec}."
            )
            raise ValueError("No supported versions")


def get_all_plugin_versions(
    session: requests.Session,
    php_version: str,
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
) -> typ.Tuple[typ.Optional[str], typ.Collection[str]]:
    resp = plugin_request(
        session,
        f"{API_URL}/api/2.0/plugins/{name.lower()}/info?coreVersion={matomo_version}",
        license_key=license_key,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("isDownloadable", False):
        return (None, [])
    latest_version = data.get("latestVersion", None)
    all_versions = []
    filtered_versions = []
    for version_data in data.get("versions", []):
        version = version_data.get("name")
        all_versions.append(version)
        if "piwik" in version_data.get("requires", {}):
            matomo_spec = SpecifierSet(version_data["requires"]["piwik"])
            if matomo_version not in matomo_spec:
                continue
        if "php" in version_data.get("requires", {}):
            php_spec = SpecifierSet(version_data["requires"]["php"])
            if php_version not in php_spec:
                continue
        filtered_versions.append(version)
    if latest_version not in all_versions:
        return None, filtered_versions
    elif latest_version not in filtered_versions:
        click.echo(
            "The latest version of {name} is not supported on Matomo {matomo_version} and PHP {php_version}."
        )
        return None, filtered_versions
    else:
        return latest_version, filtered_versions
