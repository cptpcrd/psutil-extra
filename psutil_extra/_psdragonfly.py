# Type checkers don't like the resource names not existing.
# mypy: ignore-errors
# pytype: disable=module-attr
# pylint: disable=no-member
import os
import resource
from typing import List, Tuple

import psutil

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


def proc_getgroups(pid: int) -> List[int]:
    try:
        with open(os.path.join(psutil.PROCFS_PATH, str(pid), "status")) as file:
            return list(map(int, file.read().split(" ")[13].split(",")[1:]))
    except FileNotFoundError:
        raise psutil.NoSuchProcess(pid)


def proc_get_rlimit(pid: int, res: int) -> Tuple[int, int]:
    try:
        res_name = RESOURCE_NAMES[res]
    except KeyError:
        raise ValueError("invalid resource specified")

    try:
        with open(os.path.join(psutil.PROCFS_PATH, str(pid), "rlimit")) as file:
            for line in file:
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
    except FileNotFoundError:
        raise psutil.NoSuchProcess(pid)
