import os


def proc_getpgid(pid: int) -> int:
    if pid <= 0:
        raise ProcessLookupError

    return os.getpgid(pid)


def proc_getsid(pid: int) -> int:
    if pid <= 0:
        raise ProcessLookupError

    return os.getsid(pid)
