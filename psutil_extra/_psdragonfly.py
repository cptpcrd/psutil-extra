# Type checkers don't like the resource names not existing.
# mypy: ignore-errors
# pytype: disable=module-attr
# pylint: disable=no-member
import os
import resource
from typing import List, Tuple

from . import _cache, _psposix, _util

RESOURCE_NAMES = {
    resource.RLIMIT_CPU: "cpu",
    resource.RLIMIT_FSIZE: "fsize",
    resource.RLIMIT_DATA: "data",
    resource.RLIMIT_STACK: "stack",
    resource.RLIMIT_CORE: "core",
    resource.RLIMIT_RSS: "rss",
    resource.RLIMIT_MEMLOCK: "memlock",
    resource.RLIMIT_NPROC: "nproc",
    resource.RLIMIT_NOFILE: "nofile",
    resource.RLIMIT_SBSIZE: "sbsize",
    resource.RLIMIT_AS: "vmem",
    resource.RLIMIT_POSIXLOCKS: "posixlock",
}


@_cache.CachedByPid
def _get_proc_status_text(pid: int):
    try:
        with open(os.path.join(_util.get_procfs_path(), str(pid), "status")) as file:
            return file.read()
    except FileNotFoundError:
        raise ProcessLookupError


@_cache.CachedByPid
def _get_proc_rlimit_text(pid: int):
    try:
        with open(os.path.join(_util.get_procfs_path(), str(pid), "rlimit")) as file:
            return file.read()
    except FileNotFoundError:
        raise ProcessLookupError


def proc_getgroups(pid: int) -> List[int]:
    return list(map(int, _get_proc_status_text(pid).split(" ")[13].split(",")[1:]))


def proc_get_rlimit(pid: int, res: int) -> Tuple[int, int]:
    try:
        res_name = RESOURCE_NAMES[res]
    except KeyError:
        raise ValueError("invalid resource specified")

    for line in _get_proc_rlimit_text(pid).splitlines():
        name, lim_cur_str, lim_max_str = line.split()

        if name == res_name:
            lim_cur = int(lim_cur_str)
            if lim_cur == -1:
                lim_cur = resource.RLIM_INFINITY

            lim_max = int(lim_max_str)
            if lim_max == -1:
                lim_max = resource.RLIM_INFINITY

            return lim_cur, lim_max

    raise ValueError("invalid resource specified")


proc_getpgid = _psposix.proc_getpgid
proc_getsid = _psposix.proc_getsid
