import errno
import os
import resource
from typing import List, Optional, Tuple, no_type_check

from . import _cache, _ffi, _psposix, _util


@_cache.CachedByPid
def _get_proc_status_text(pid: int) -> str:
    try:
        with open(os.path.join(_util.get_procfs_path(), str(pid), "status")) as file:
            return file.read()
    except FileNotFoundError:
        raise ProcessLookupError


def _get_proc_status_field(pid: int, name: str) -> str:
    for line in _get_proc_status_text(pid).splitlines():
        if line.startswith(name + ":\t"):
            return line[len(name) + 2:].rstrip("\n")

    raise ValueError


def proc_getgroups(pid: int) -> List[int]:
    return list(map(int, _get_proc_status_field(pid, "Groups").split()))


def proc_get_umask(pid: int) -> int:
    try:
        umask_str = _get_proc_status_field(pid, "Umask")
    except ValueError:
        raise _ffi.build_oserror(errno.ENOTSUP)

    return int(umask_str, 8)


@no_type_check
def proc_rlimit(
    pid: int, res: int, new_limits: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    if pid == 0:
        # prlimit() treats pid=0 specially.
        # psutil doesn't, so we don't either.
        raise ProcessLookupError

    if new_limits is None:
        return resource.prlimit(  # pytype: disable=missing-parameter  # pylint: disable=no-member
            pid, res
        )
    else:
        return resource.prlimit(pid, res, new_limits)  # pylint: disable=no-member


proc_getrlimit = proc_rlimit

proc_getpgid = _psposix.proc_getpgid
proc_getsid = _psposix.proc_getsid
