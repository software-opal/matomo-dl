import random
import subprocess
import tempfile


class GPGVerifier:

    keyservers = frozenset(
        ('keys.gnupg.net', 'keyserver.ubuntu.com', 'pgp.mit.edu'))

    def __init__(self):
        self.tmp_folder = None

    def __enter__(self):
        if self.tmp_folder is None:
            self.tmp_folder = tempfile.NamedTemporaryFile()
            self.tmp_folder.__enter__()
        return self

    def __exit__(self):
        if self.tmp_folder is not None:
            self.tmp_folder.__exit__()
        self.tmp_folder = None

    def get_tmp_folder(self):
        if self.tmp_folder:
            return self.tmp_folder.name
        else:
            return self.__enter__().get_tmp_folder()

    def gpg_call(self, *args, check=True, **kwargs):
        args = ('gpg', '--batch', '--no-default-keyring',
                '--keyring', self.get_tmp_folder()) + args
        return subprocess.run(args, check=check, **kwargs)

    def load_fingerprint(self, fingerprint):
        err = None
        for attempt in range(3):
            key_server = random.choice(list(self.keyservers))
            try:
                self.gpg_call('--keyserver', key_server,
                              '--recv-keys', fingerprint)
                return
            except subprocess.CalledProcessError as e:
                err = e
        raise err

    def load_public_key(self, key_content):
        self.gpg_call('--import', '-', input=key_content)

    def verify(self, data, signature):
        with tempfile.NamedTemporaryFile() as data_file:
            data_file.write(data)
            data_file.flush()
            self.gpg_call('--verify', '-', data_file.name, input=signature)
