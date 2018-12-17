from contextlib import contextmanager
import tempfile
import os
import hashlib
import pathlib
import typing as typ
import zipfile
import shutil
import requests

MATOMO_ZIP_SHA1S = {"3.6.1": "59daaf90805c98de006db28fa297f01e1dd235ce"}
TEST_CACHE = pathlib.Path(__file__).parent.parent / ".test_cache"


def download_matomo_zip(version: str, f: typ.IO):
    expected_sha = MATOMO_ZIP_SHA1S[version]
    with requests.get(
        f"https://builds.matomo.org/matomo-{version}.zip", stream=True
    ) as r:
        r.raise_for_status()
        hasher = hashlib.sha1()
        for data in r.iter_content(chunk_size=1024 * 1024):
            if data:
                f.write(data)
                hasher.update(data)
        print(hasher.hexdigest())
        assert expected_sha == hasher.hexdigest()
    f.seek(0, os.SEEK_SET)


def dowload_cache_matomo_zip(version, f: typ.IO):
    target = TEST_CACHE / f"matomo-v{version}.zip"
    expected_sha = MATOMO_ZIP_SHA1S[version]
    if target.exists():
        hasher = hashlib.sha1()
        with target.open("rb") as test:
            while True:
                data = test.read(1024 * 1024)
                if not data:
                    break
                hasher.update(data)
        if expected_sha == hasher.hexdigest():
            with target.open("rb") as zip_f:
                shutil.copyfileobj(zip_f, f)
            return
        else:
            target.unlink()
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
    tmp_target = target.with_suffix(".zip.tmp")
    if tmp_target.exists():
        tmp_target.unlink()
    with tmp_target.open("wb") as temp_f:
        download_matomo_zip(version, temp_f)
    tmp_target.rename(target)
    with target.open("rb") as zip_f:
        shutil.copyfileobj(zip_f, f)


@contextmanager
def with_matomo_zip(version: str):
    with tempfile.NamedTemporaryFile() as f:
        # with open(f"matomo-v{version}.zip", 'wb') as f:
        dowload_cache_matomo_zip(version, f)
        yield f


@contextmanager
def with_extracted_matomo(version: str):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d)
        with with_matomo_zip(version) as f, zipfile.ZipFile(f, "r") as z:
            for name in z.namelist():
                if not name.startswith("matomo/"):
                    continue
                if name[-1] == "/":
                    continue
                _, _, target_name = name.partition("/")
                target = p / target_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfileobj(z.open(name), target.open("wb"))
        yield p
