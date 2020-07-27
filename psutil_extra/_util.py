import dataclasses
import resource
from typing import Set, cast

import psutil

RESOURCE_NUMS = set()
for name in dir(resource):
    if name.startswith("RLIMIT_"):
        RESOURCE_NUMS.add(getattr(resource, name))


@dataclasses.dataclass
class ProcessSignalMasks:
    pending: Set[int]
    blocked: Set[int]
    ignored: Set[int]
    caught: Set[int]


def check_rlimit_resource(res: int) -> None:
    if res not in RESOURCE_NUMS:
        raise ValueError("invalid resource specified")


def get_procfs_path() -> str:
    return cast(str, getattr(psutil, "PROCFS_PATH", "/proc"))


def expand_sig_bitmask(mask: int) -> Set[int]:
    # It seems that every OS uses the same binary representation
    # for signal sets. Only the size varies.

    res = set()
    sig = 1  # Bit 0 in the mask corresponds to signal 1

    while mask:
        if mask & 1:
            res.add(sig)

        mask >>= 1
        sig += 1

    return res
