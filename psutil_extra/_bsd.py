import ctypes
from typing import Collection, Union

from . import _ffi

libc = _ffi.load_libc()

libc.sysctl.argtypes = (
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_uint,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_size_t),
    ctypes.c_void_p,
    ctypes.c_size_t,
)
libc.sysctl.restype = ctypes.c_int


def sysctl(
    mib: Collection[int],
    new: Union[None, bytes, ctypes.Array, ctypes.Structure],  # type: ignore
    old: Union[None, ctypes.Array, ctypes.Structure],  # type: ignore
) -> int:
    raw_mib = (ctypes.c_int * len(mib))(*mib)  # pytype: disable=not-callable

    if new is None:
        new_size = 0
        raw_new = None
    elif isinstance(new, bytes):
        new_size = len(new)
        raw_new = ctypes.byref(ctypes.create_string_buffer(new))
    else:
        new_size = ctypes.sizeof(new)
        raw_new = ctypes.byref(new)

    if old is None:
        old_size = ctypes.c_size_t(0)
        raw_old = None
    else:
        old_size = ctypes.c_size_t(ctypes.sizeof(old))
        raw_old = ctypes.byref(old)

    if libc.sysctl(raw_mib, len(mib), raw_old, ctypes.byref(old_size), raw_new, new_size) < 0:
        raise _ffi.build_oserror(ctypes.get_errno())

    return old_size.value
