import re
import tarfile
import typing as typ
from io import BytesIO
from urllib.parse import urljoin

import requests

import bs4

from ..distribution.lock import MatomoLock
from ..distribution.version import Version
from ..gpg import GPGVerifier
from ..session import SessionStore

API_URL = "http://api.matomo.org"
BUILDS_URL = "https://builds.matomo.org"
VERSION_REGEX = re.compile(
    r'.*\/matomo-([0-9]+.*)\.((?:zip|tar\.gz)(?:\.asc)?)$')


def sync_matomo_lock(session: SessionStore, version_spec: Version, existing_lock: typ.Optional[MatomoLock]) -> MatomoLock:
    version = resolve_matomo_version_spec(session, version_spec)
    if existing_lock and version == existing_lock.version:
        return existing_lock
    cache_key = 'matomo-{}-tarball'.format(version)
    url, data = get_matomo_version(session, version)
    base_path = get_extraction_root(data, 'piwik.php')
    hashes = session.store_cache_data(cache_key, data)
    return MatomoLock(version=version, link=url, hashes=hashes, extraction_root=base_path)


def get_matomo_version(session: requests.Session, version: str) -> typ.Tuple[str, bytes]:
    dl_url = '{}/matomo-{}.tar.gz'.format(BUILDS_URL, version)
    asc_url = '{}/matomo-{}.tar.gz.asc'.format(BUILDS_URL, version)

    r = session.get(dl_url)
    r.raise_for_status()
    tarball = r.content
    r = session.get(asc_url)
    r.raise_for_status()
    tarball_sig = r.content
    verifier = GPGVerifier()
    verifier.load_fingerprint('0x814E346FA01A20DBB04B6807B5DBD5925590A237')
    verifier.verify(tarball, tarball_sig)
    return dl_url, tarball


def get_extraction_root(tarball, root_file) -> typ.Optional[str]:
    if root_file[0:2] == './':
        root_file = root_file[2:]
    root_file = root_file.lstrip('/')
    root = None
    with tarfile.open(file_obj=BytesIO(tarball)) as tar:
        for name in tar.getnames():
            root_folder, file, _ = name.rpartition(root_file)
            if file == root_file and root_folder[-1] == '/':
                if root is None:
                    root = root_file
                elif len(root) > len(root_file):
                    root = root_file
    return root


def resolve_matomo_version_spec(session: requests.Session, version_spec: Version) -> str:
    if version_spec.matches_one_only:
        return version_spec.version

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


def get_latest_matomo_version(session: requests.Session):
    resp = session.get(API_URL + '/1.0/getLatestVersion/')
    resp.raise_for_status()
    return resp.text


def get_all_matomo_versions(session: requests.Session) -> typ.Collection[str]:
    resp = session.get(BUILDS_URL)
    resp.raise_for_status()
    base_url = resp.url
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    versions = set()
    for a in soup.find_all('a'):
        if 'href' not in a.attrs or 'matomo' not in a.attrs['href']:
            continue
        full_link = urljoin(base_url, a.attrs['href'])
        match = VERSION_REGEX.match(full_link)
        if match:
            versions.add(match.group(1))
    return set(versions)
