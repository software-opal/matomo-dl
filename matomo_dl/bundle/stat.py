import stat

user_execute_bit = stat.S_IXUSR


def is_mode_executable(mode: int) -> bool:
    return (stat.S_IMODE(mode) & 0o111) != 0


def standardise_mode(mode: int, *, force_exec: bool = False) -> int:
    if force_exec or is_mode_executable(mode):
        # User has full read/write/execute. Others have read/execute
        return 0o755
    else:
        # User has full read/write. Others have read
        return 0o644


def standardise_privacy_mode(mode: int, *, force_exec: bool = False) -> int:
    return standardise_mode(mode, force_exec=force_exec) & 0o700


def standardise_extended_mode(ext_mode: int) -> int:
    file_type = stat.S_IFMT(ext_mode)
    return file_type | standardise_mode(ext_mode, force_exec=stat.S_ISDIR(file_type))


def is_extended_mode_dir(ext_mode: int) -> bool:
    return stat.S_ISDIR(ext_mode)
