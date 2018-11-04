import logging
import pathlib
import typing as typ
from datetime import timedelta
from types import MappingProxyType

from .caching_store import CachingSessionStore
from .store import SessionStore

logger = logging.getLogger(__name__)
CACHE_LEVEL_NAMES = MappingProxyType(
    {"none": 0, "locks": 1, "memory": 2, "persist": 3, "persistant": 3, "persistent": 3}
)

if CachingSessionStore is None:
    SUPPORTED_CACHE_LEVEL_NAMES = frozenset(("none", "locks"))
else:
    SUPPORTED_CACHE_LEVEL_NAMES = frozenset(("none", "locks", "memory", "persist"))

SUPPORTED_CACHE_LEVELS = frozenset(
    CACHE_LEVEL_NAMES[name] for name in SUPPORTED_CACHE_LEVEL_NAMES
)
MAX_SUPPORTED_CACHE_LEVEL = max(SUPPORTED_CACHE_LEVELS)
DEFAULT_CACHE_LEVEL = min(2, MAX_SUPPORTED_CACHE_LEVEL)


def create_session(
    cache_dir: typ.Union[pathlib.Path, str, None],
    level: typ.Union[str, int, float, None],
    clear: bool = False,
) -> SessionStore:
    cache_level = standardise_level(level)
    del level  # Prevent bugs if we accidentally reuse `level`
    if not cache_dir or cache_level == 0:
        return SessionStore(cache_dir=None)
    else:
        cache_dir = pathlib.Path(cache_dir)
        cache_dir.resolve(strict=False)
        if clear:
            remove_dir(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        if cache_level == CACHE_LEVEL_NAMES["memory"]:
            return create_cached_session_store(cache_dir=cache_dir, backend="memory")
        elif cache_level == CACHE_LEVEL_NAMES["persistent"]:
            return create_cached_session_store(cache_dir=cache_dir, backend="sqlite")
        else:
            return SessionStore(cache_dir=cache_dir)


def create_cached_session_store(cache_dir: pathlib.Path, backend: str) -> SessionStore:
    if not CachingSessionStore:
        logger.warning(
            "CachingSessionStore is unavaliable due to a "
            "lack of the underlying library."
        )
        return SessionStore(cache_dir=cache_dir)
    common = {
        "allowable_methods": ["GET", "POST"],
        "old_data_on_error": False,
        "expire_after": timedelta(days=7),
    }
    if backend == "memory":
        return CachingSessionStore(cache_dir=cache_dir, backend="memory", **common)
    else:
        return CachingSessionStore(
            cache_dir=cache_dir,
            cache_name=str(cache_dir / "request-cache"),  # requests_cache argument
            backend_options={"fast_save": True},
            backend="sqlite",
            **common,
        )


def standardise_level(level: typ.Union[str, int, float, None]) -> int:
    if level is None:
        return DEFAULT_CACHE_LEVEL
    elif str(level) in CACHE_LEVEL_NAMES:
        cache_level = CACHE_LEVEL_NAMES[str(level)]
    else:
        cache_level = int(level)
    if cache_level < 0:
        cache_level = 0
    elif cache_level > max(CACHE_LEVEL_NAMES.values()):
        logger.warning(
            f"The given level {level}(mapped to {cache_level}) is outside "
            f"the supported range. Clamping to {MAX_SUPPORTED_CACHE_LEVEL}"
        )
        cache_level = MAX_SUPPORTED_CACHE_LEVEL
    if cache_level not in SUPPORTED_CACHE_LEVELS:
        logger.warning(
            f"The given level {level!r}(mapped to {cache_level}) is not supported, "
            f"likely due to missing libraries. Setting to {DEFAULT_CACHE_LEVEL}"
        )
        cache_level = DEFAULT_CACHE_LEVEL
    assert 0 <= cache_level <= MAX_SUPPORTED_CACHE_LEVEL
    return cache_level


def remove_dir(input_path: pathlib.Path):
    if not input_path.exists():
        return
    if input_path.is_symlink() or input_path.is_file():
        input_path.unlink()
        return
    to_explore = [input_path]
    while to_explore:
        curr = to_explore[-1]
        old_len = len(to_explore)
        assert not curr.is_symlink() and curr.is_dir()
        for path in curr.iterdir():
            if path.is_symlink() or path.is_file():
                path.unlink()
            if path.is_dir():
                to_explore.append(path)
        if old_len == len(to_explore):
            curr.rmdir()
            to_explore.pop()
