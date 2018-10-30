import functools
import hashlib
import typing as typ

HashInfo = str


desired_algorithms = ["sha256"]


def all_hashes_for_data(data: bytes) -> HashInfo:
    return ":".join(next(hashes_for_data(data)))


def hashes_for_data(data: bytes) -> typ.Iterator[typ.Tuple[str, str]]:
    hashed = False
    for algo in desired_algorithms:
        if algo in hashlib.algorithms_available:
            hashed = True
            yield (algo, hashlib.new(algo, data).hexdigest())
    assert hashed


@functools.lru_cache()
def hash_for_data(data: bytes, algo: str) -> str:
    assert algo in hashlib.algorithms_available
    return hashlib.new(algo, data).hexdigest()
