import logging
import typing as typ

from matomo_dl.bundle.extract import extract_zip_file
from matomo_dl.bundle.info import BuildInformation
from matomo_dl.distribution.lock import VersionedPluginLock
from matomo_dl.errors import DownloadHashMismatch
from matomo_dl.lock.plugin.versioned import (
    get_cache_key,
    get_plugin_data,
    plugin_request,
)
from matomo_dl.progress import progressbar
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)


def extract_plugins(
    session: SessionStore, license_key: typ.Optional[str], build: BuildInformation
):
    plugin_locks = build.lockfile.plugin_locks
    with progressbar(plugin_locks.items(), label="Extracting plugins") as bar:
        for name, plugin_lock in bar:
            if isinstance(plugin_lock, VersionedPluginLock):
                extract_versioned_plugin(session, license_key, build, name, plugin_lock)
            else:
                raise ValueError()


def extract_versioned_plugin(
    session: SessionStore,
    license_key: typ.Optional[str],
    build: BuildInformation,
    name: str,
    lock: VersionedPluginLock,
):
    plugin = get_plugin_data(session, license_key, name)
    plugin.assert_downloadable()  # We perform a license check every build.
    cache_key = get_cache_key(name, lock.version)

    data = session.retrieve_cache_data(cache_key, lock.hash)
    if not data:
        r = plugin_request(session, lock.link, license_key=license_key)
        data = r.content
        assert data is not None
        data_hash = session.store_cache_data(cache_key, data)
        if lock.hash != data_hash:
            raise DownloadHashMismatch()

    latest_mtime = extract_zip_file(
        data, build.folder / "plugins" / plugin.name, root=lock.extraction_root
    )
    assert latest_mtime is not None
    build.add_source_time(latest_mtime)
