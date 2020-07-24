import ctypes
import errno
from typing import Optional, Tuple

import psutil

from . import _bsd, _ffi

CTL_PROC = 1
PROC_PID_LIMIT = 2
PROC_PID_LIMIT_TYPE_SOFT = 1
PROC_PID_LIMIT_TYPE_HARD = 2

rlim_t = ctypes.c_uint64  # pylint: disable=invalid-name


def _proc_rlimit_getset(pid: int, res: int, new_limit: Optional[int], hard: bool) -> int:
    new_limit_raw = ctypes.byref(rlim_t(new_limit)) if new_limit is not None else None
    old_limit = rlim_t(0)

    try:
        _bsd.sysctl_raw(  # pytype: disable=wrong-arg-types
            [
                CTL_PROC,
                pid,
                PROC_PID_LIMIT,
                res + 1,
                (PROC_PID_LIMIT_TYPE_HARD if hard else PROC_PID_LIMIT_TYPE_SOFT),
            ],
            new_limit_raw,  # type: ignore
            ctypes.byref(old_limit),  # type: ignore
        )
    except OSError as ex:
        if ex.errno == errno.ENOENT:
            raise psutil.NoSuchProcess(pid)
        else:
            raise

    return old_limit.value


def proc_rlimit(
    pid: int, res: int, new_limits: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    if pid <= 0:
        raise psutil.NoSuchProcess(pid)

    new_soft: Optional[int]
    new_hard: Optional[int]
    if new_limits is not None:
        new_soft = new_limits[0]
        new_hard = new_limits[1]
        if new_soft > new_hard:
            raise _ffi.build_oserror(errno.EINVAL)
    else:
        new_soft = None
        new_hard = None

    old_soft: Optional[int]
    try:
        old_soft = _proc_rlimit_getset(pid, res, new_soft, False)
    except OSError as ex:
        if ex.errno == errno.EINVAL:
            old_soft = None
        else:
            raise

    old_hard = _proc_rlimit_getset(pid, res, new_hard, True)

    if old_soft is None:
        old_soft = _proc_rlimit_getset(pid, res, new_soft, False)

    return old_soft, old_hard


proc_getrlimit = proc_rlimit
