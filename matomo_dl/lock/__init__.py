import typing as typ
import zipfile
from io import BytesIO


def get_extraction_root(zip_data, root_file) -> typ.Optional[str]:
    if root_file[0:2] == "./":
        root_file = root_file[2:]
    root_file = root_file.lstrip("/")
    root = None
    with zipfile.ZipFile(BytesIO(zip_data)) as tar:
        for name in tar.namelist():
            root_folder, file, _ = name.rpartition(root_file)
            if file == root_file and root_folder[-1] == "/":
                if root is None:
                    root = root_file
                elif len(root) > len(root_file):
                    root = root_file
    return root
