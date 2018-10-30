from .store import SessionStore

try:
    from requests_cache.core import CachedSession

    class CachingSessionStore(SessionStore, CachedSession):
        pass


except ImportError:
    CachingSessionStore = None
