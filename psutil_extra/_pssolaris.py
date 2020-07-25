# pylint: disable=invalid-name
import contextlib
import ctypes
import errno
from typing import Iterator, List

import psutil

from . import _ffi

pid_t = ctypes.c_int
gid_t = ctypes.c_uint32

libc = _ffi.load_libc()

libc.ucred_get.argtypes = (pid_t,)
libc.ucred_get.restype = ctypes.c_void_p

libc.ucred_getgroups.argtypes = (
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(gid_t)),  # pytype: disable=invalid-typevar
)
libc.ucred_getgroups.restype = ctypes.c_int

libc.ucred_free.argtypes = (ctypes.c_void_p,)
libc.ucred_free.restype = None


@contextlib.contextmanager
def _get_ucred(pid: int) -> Iterator[ctypes.c_void_p]:
    raw_ucred = libc.ucred_get(pid)
    if not raw_ucred.value:
        raise _ffi.build_oserror(ctypes.get_errno())

    try:
        yield raw_ucred
    finally:
        libc.ucred_free(raw_ucred)


def proc_getgroups(pid: int) -> List[int]:
    if pid <= 0:
        raise psutil.NoSuchProcess(pid)

    with _get_ucred(pid) as raw_ucred:
        groups_ptr = ctypes.POINTER(gid_t)()  # pytype: disable=not-callable
        ngroups = libc.ucred_getgroups(raw_ucred, ctypes.pointer(groups_ptr))
        if ngroups < 0:
            raise _ffi.build_oserror(errno.EINVAL)

        return [groups_ptr[i].value for i in range(ngroups)]
