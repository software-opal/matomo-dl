import logging
import typing as typ


from matomo_dl.distribution.lock import GitPluginLock
from matomo_dl.session import SessionStore

logger = logging.getLogger(__name__)


def sync_git_plugin_lock(
    session: SessionStore,
    php_version: str,
    matomo_version: str,
    license_key: typ.Optional[str],
    name: str,
    git_url: str,
    ref: typ.Optional[str],
    existing_lock: typ.Optional[GitPluginLock],
) -> GitPluginLock:
    pass
