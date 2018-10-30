import logging
import re
import typing as typ
from urllib.parse import urljoin

import bs4
import requests

from matomo_dl.distribution.lock import MatomoLock
from matomo_dl.distribution.version import Version
from matomo_dl.gpg import GpgVerifier, KeyImportError, VerificationError
from matomo_dl.lock import get_extraction_root
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)
API_URL = "https://api.matomo.org"
BUILDS_URL = "https://builds.matomo.org"
VERSION_REGEX = re.compile(r".*\/matomo-([0-9]+.*)\.((?:zip|tar\.gz)(?:\.asc)?)$")


def sync_matomo_lock(
    session: SessionStore,
    version_spec: Version,
    existing_lock: typ.Optional[MatomoLock],
) -> MatomoLock:
    version = resolve_matomo_version_spec(session, version_spec)
    if existing_lock and version == existing_lock.version:
        return existing_lock
    cache_key = f"matomo-{version}-zip"
    url, data = get_matomo_version(session, version)
    base_path = get_extraction_root(data, "piwik.php")
    if not base_path:
        logger.error("Cannot determine how to extract Matomo!")
        raise ValueError("")
    hash = session.store_cache_data(cache_key, data)
    return MatomoLock(version=version, link=url, hash=hash, extraction_root=base_path)


def get_matomo_version(
    session: requests.Session, version: str
) -> typ.Tuple[str, bytes]:
    dl_url = f"{BUILDS_URL}/matomo-{version}.zip"
    asc_url = f"{BUILDS_URL}/matomo-{version}.zip.asc"
    logger.info(f"Downloading Matomo release {version}")
    r = session.get(dl_url)
    zip_file = r.content
    r = session.get(asc_url)
    r.raise_for_status()
    zip_file_sig = r.content

    with GpgVerifier() as verifier:
        try:
            verifier.load_fingerprint("0x814E346FA01A20DBB04B6807B5DBD5925590A237")
            verifier.verify(zip_file, zip_file_sig)
        except KeyImportError:
            logger.error("Unable to import the Matomo release keys.")
            raise
        except VerificationError:
            logger.error("Signature does not match file.")
            raise
    return dl_url, zip_file


def resolve_matomo_version_spec(
    session: requests.Session, version_spec: Version
) -> str:
    latest = get_latest_matomo_version(session)
    if version_spec.choose_version([latest]):
        return latest
    else:
        all_versions = get_all_matomo_versions(session)
        version = version_spec.choose_version(set(all_versions))
        if version:
            return version
        else:
            raise ValueError("No supported versions")


def get_latest_matomo_version(session: requests.Session) -> str:
    resp = session.get(f"{API_URL}/1.0/getLatestVersion/")
    resp.raise_for_status()
    return resp.text.strip()


def get_all_matomo_versions(session: requests.Session) -> typ.Collection[str]:
    resp = session.get(BUILDS_URL)
    resp.raise_for_status()
    base_url = resp.url
    soup = bs4.BeautifulSoup(resp.text, "lxml")
    versions = set()
    for a in soup.find_all("a"):
        if "href" not in a.attrs or "matomo" not in a.attrs["href"]:
            continue
        full_link = urljoin(base_url, a.attrs["href"])
        match = VERSION_REGEX.match(full_link)
        if match:
            versions.add(match.group(1))
    return set(versions)
