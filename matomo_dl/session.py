import pathlib
import re
import typing as typ

import requests
from requests.adapters import HTTPAdapter

from .hashing import HashInfo, all_hashes_for_data, hashes_for_data


class HttpLoggingAdapter(HTTPAdapter):

    def send(self, request, *a, **k):
        if request.url.startswith('http://'):
            print("WARNING: Request sent over HTTP.\n\t{}".format(request.url))
        return super().send(request, *a, **k)


class SessionStore(requests.Session):

    def __init__(self, *a, cache_folder, **k):
        super().__init__(*a, **k)
        self.mount("http://", HttpLoggingAdapter())
        self.cache_folder = pathlib.Path(cache_folder)

    def store_cache_data(self, cache_key: str, data: bytes) -> HashInfo:
        assert re.match(r'^[0-9a-z\-_.]+$', cache_key)
        file = self.cache_folder / "{}.dat".format(cache_key)
        file.write_bytes(data)
        hash_file = self.cache_folder / "{}.dat.check".format(cache_key)
        hashes = all_hashes_for_data(data)
        hash_file.write('\n'.join(
            '{}:{}'.format(algo, val)
            for algo, val in hashes.items()
        ))
        return hashes

    def retrieve_cache_data(self, cache_key: str, expected_hashes: typ.Mapping[str, str]) -> typ.Tuple[typ.Optional[bytes], HashInfo]:
        assert re.match(r'^[0-9a-z\-_.]+$', cache_key)
        assert expected_hashes
        file = self.cache_folder / "{}.dat".format(cache_key)
        hash_file = self.cache_folder / "{}.dat.check".format(cache_key)
        if not file.exists() or not hash_file.exists():
            return None, {}
        digests = {}
        for hash_line in hash_file.read_text().splitlines():
            algo, _, digest = hash_line.rpartition(':')
            if digest:
                digests[algo] = digest
        has_match = False
        for algo, digest in digests:
            if expected_hashes.get(algo) == digest:
                has_match = True
                break
        if has_match:
            data = file.read_bytes()
            for algo, digest in hashes_for_data(data):
                if expected_hashes.get(algo) == digest:
                    return data, digests
        file.delete()
        hash_file.delete()
        return None, {}
