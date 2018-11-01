import tarfile
import typing as typ
import zipfile
from io import BytesIO


def get_zip_extraction_root(zip_data, root_file) -> typ.Optional[str]:
    if root_file[0:2] == "./":
        root_file = root_file[2:]
    root_file = root_file.lstrip("/")
    root = None
    with zipfile.ZipFile(BytesIO(zip_data)) as zipf:
        for name in zipf.namelist():
            root_folder, file, _ = name.rpartition(root_file)
            if file == root_file and root_folder[-1] == "/":
                if root is None:
                    root = root_folder
                elif len(root) > len(root_file):
                    root = root_folder
    return root


def get_tar_extraction_root(tar_data, root_file) -> typ.Optional[str]:
    if root_file[0:2] == "./":
        root_file = root_file[2:]
    root_file = root_file.lstrip("/")
    root = None
    with tarfile.open(fileobj=BytesIO(tar_data)) as tar:
        for name in tar.getnames():
            root_folder, file, _ = name.rpartition(root_file)
            if file == root_file and root_folder[-1] == "/":
                if root is None:
                    root = root_file
                elif len(root) > len(root_file):
                    root = root_file
    return root
