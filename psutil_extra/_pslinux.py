import errno
import os
import resource
from typing import List, Optional, Tuple, no_type_check

import psutil

from . import _ffi


def _get_proc_status(pid: int, name: str) -> str:
    try:
        with open(os.path.join(psutil.PROCFS_PATH, str(pid), "status")) as file:
            for line in file:
                if line.startswith(name + ":\t"):
                    return line[len(name) + 2:].rstrip("\n")

    except FileNotFoundError:
        raise psutil.NoSuchProcess(pid)

    raise ValueError


def proc_getgroups(pid: int) -> List[int]:
    return list(map(int, _get_proc_status(pid, "Groups").split()))


def proc_get_umask(pid: int) -> int:
    try:
        umask_str = _get_proc_status(pid, "Umask")
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
        raise psutil.NoSuchProcess(pid)

    if new_limits is None:
        return resource.prlimit(  # pytype: disable=missing-parameter  # pylint: disable=no-member
            pid, res
        )
    else:
        return resource.prlimit(pid, res, new_limits)  # pylint: disable=no-member


proc_getrlimit = proc_rlimit
