import dataclasses
import errno
import os
import resource
from typing import Dict, List, Optional, Set, Tuple, no_type_check

from . import _cache, _ffi, _psposix, _util


@dataclasses.dataclass
class ProcessSignalMasks(_util.ProcessSignalMasks):
    process_pending: Set[int]


def parse_sigmask(raw_mask: str) -> Set[int]:
    return _util.expand_sig_bitmask(int(raw_mask, 16))


@_cache.CachedByPid
def _get_proc_status_dict(pid: int) -> Dict[str, str]:
    try:
        res = {}

        with open(os.path.join(_util.get_procfs_path(), str(pid), "status")) as file:
            for line in file:
                name, value = line.split(":\t", maxsplit=1)
                res[name] = value.rstrip("\n")

        return res
    except FileNotFoundError:
        raise ProcessLookupError


def proc_getgroups(pid: int) -> List[int]:
    return list(map(int, _get_proc_status_dict(pid)["Groups"].split()))


def proc_get_umask(pid: int) -> int:
    try:
        umask_str = _get_proc_status_dict(pid)["Umask"]
    except KeyError:
        raise _ffi.build_oserror(errno.ENOTSUP)
    else:
        return int(umask_str, 8)


def proc_get_sigmasks(pid: int) -> ProcessSignalMasks:
    proc_status = _get_proc_status_dict(pid)

    return ProcessSignalMasks(  # pytype: disable=wrong-keyword-args
        process_pending=parse_sigmask(proc_status["ShdPnd"]),
        pending=parse_sigmask(proc_status["SigPnd"]),
        blocked=parse_sigmask(proc_status["SigBlk"]),
        ignored=parse_sigmask(proc_status["SigIgn"]),
        caught=parse_sigmask(proc_status["SigCgt"]),
    )


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
