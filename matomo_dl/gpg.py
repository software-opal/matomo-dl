import random
import shutil
import subprocess  # noqa: S404 -- subprocess usage is safe
import tempfile
import typing as typ


class GpgError(Exception):
    pass


class KeyImportError(GpgError):
    pass


class VerificationError(GpgError):
    pass


class GpgVerifier:

    keyservers = frozenset(("keys.gnupg.net", "keyserver.ubuntu.com", "pgp.mit.edu"))

    tmp_folder: typ.Optional[tempfile.TemporaryDirectory] = None

    def __enter__(self) -> "GpgVerifier":
        if self.tmp_folder is None:
            self.tmp_folder = tempfile.TemporaryDirectory()
            self.tmp_folder.__enter__()
        return self

    def __exit__(self, ex_type, value, traceback):
        if self.tmp_folder is not None:
            # Occasional race condition may cause files in the tem directory to
            # disappear during the removal. Just do the best we can
            name = self.tmp_folder.name
            try:
                self.tmp_folder.__exit__(ex_type, value, traceback)
            except IOError:
                try:
                    shutil.rmtree(name, ignore_errors=True)
                except IOError:
                    pass
        self.tmp_folder = None

    def get_tmp_folder(self) -> str:
        if self.tmp_folder:
            return self.tmp_folder.name
        else:
            return self.__enter__().get_tmp_folder()

    def gpg_call(self, *args: str, check=True, **kwargs: typ.Any):
        args = (
            "gpg",
            "--batch",
            "--no-default-keyring",
            "--keyring",
            self.get_tmp_folder() + "/keyring",
            "--homedir",
            self.get_tmp_folder(),
        ) + args
        kwargs.setdefault("input", "")
        return subprocess.run(  # noqa: S603 -- assume callers are safe
            args, check=check, **kwargs
        )

    def load_fingerprint(self, fingerprint: str):
        err = None
        for _attempt in range(3):
            key_server = random.choice(  # noqa: S311 -- psuedo-random is fine
                list(self.keyservers)
            )
            try:
                self.gpg_call("--keyserver", key_server, "--recv-keys", fingerprint)
                return
            except subprocess.CalledProcessError as e:
                err = e
        raise KeyImportError() from err

    def load_public_key(self, key_content: typ.Union[str, bytes]):
        try:
            self.gpg_call("--import", "-", input=key_content)
        except subprocess.CalledProcessError as e:
            raise KeyImportError() from e

    def verify(self, data: bytes, signature: bytes):
        with tempfile.NamedTemporaryFile("wb") as data_file:
            data_file.write(data)
            data_file.flush()
            try:
                self.gpg_call("--verify", "-", data_file.name, input=signature)
            except subprocess.CalledProcessError as e:
                raise VerificationError() from e
