import resource
from typing import cast

import psutil

RESOURCE_NUMS = set()
for name in dir(resource):
    if name.startswith("RLIMIT_"):
        RESOURCE_NUMS.add(getattr(resource, name))


def check_rlimit_resource(res: int) -> None:
    if res not in RESOURCE_NUMS:
        raise ValueError("invalid resource specified")


def get_procfs_path() -> str:
    return cast(str, getattr(psutil, "PROCFS_PATH", "/proc"))
