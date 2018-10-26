import collections
import functools
import hashlib
import types
import typing as typ

desired_algorithms = [
    'blake2b',
    'sha3_512',
    'sha512',
]

HashInfo = typ.Mapping[str, str]


def all_hashes_for_data(data: bytes) -> HashInfo:
    return types.MappingProxyType(collections.OrderedDict(hashes_for_data))


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
