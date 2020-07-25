import ctypes
import errno
import resource
import struct
from typing import List, Optional, Tuple

import psutil

from . import _bsd, _util

CTL_KERN = 1
KERN_PROC = 14
KERN_PROC_GROUPS = 34
KERN_PROC_RLIMIT = 37
KERN_PROC_UMASK = 39

gid_t = ctypes.c_uint32  # pylint: disable=invalid-name
gid_t_format = "=I"
rlim_t = ctypes.c_int64  # pylint: disable=invalid-name


class Rlimit(ctypes.Structure):
    _fields_ = [
        ("rlim_cur", rlim_t),
        ("rlim_max", rlim_t),
    ]

    @classmethod
    def construct_opt(cls, limits: Optional[Tuple[int, int]]) -> Optional["Rlimit"]:
        return cls(rlim_cur=limits[0], rlim_max=limits[1]) if limits is not None else None

    def unpack(self) -> Tuple[int, int]:
        return self.rlim_cur, self.rlim_max


def proc_get_umask(pid: int) -> int:
    if pid <= 0:
        raise psutil.NoSuchProcess(pid)

    umask = ctypes.c_ushort()

    _bsd.sysctl_raw(  # pytype: disable=wrong-arg-types
        [CTL_KERN, KERN_PROC, KERN_PROC_UMASK, pid], None, umask  # type: ignore
    )

    return umask.value


def proc_getgroups(pid: int) -> List[int]:
    if pid <= 0:
        raise psutil.NoSuchProcess(pid)

    while True:
        try:
            groups_bin = _bsd.sysctl([CTL_KERN, KERN_PROC, KERN_PROC_GROUPS, pid], None)
        except OSError as ex:
            if ex.errno != errno.EINVAL:
                raise
        else:
            return [gid for (gid,) in struct.iter_unpack(gid_t_format, groups_bin)]


def proc_rlimit(
    pid: int, res: int, new_limits: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    if pid <= 0:
        raise psutil.NoSuchProcess(pid)

    _util.check_rlimit_resource(res)

    new_limits_raw = Rlimit.construct_opt(new_limits)

    old_limits = Rlimit(rlim_cur=resource.RLIM_INFINITY, rlim_max=resource.RLIM_INFINITY)

    _bsd.sysctl_raw([CTL_KERN, KERN_PROC, KERN_PROC_RLIMIT, pid, res], new_limits_raw, old_limits)

    return old_limits.unpack()


proc_getrlimit = proc_rlimit
