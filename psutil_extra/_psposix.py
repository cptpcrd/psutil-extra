import os


def proc_getpgid(pid: int) -> int:
    if pid <= 0:
        raise ProcessLookupError

    return os.getpgid(pid)
