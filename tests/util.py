import os
from typing import Callable

import psutil

import psutil_extra


def fork_proc(child_func: Callable) -> psutil.Process:
    pid = os.fork()
    if pid == 0:
        try:
            child_func()
        except SystemExit as ex:
            os._exit(ex.code)
        finally:
            # Make sure we exit somehow
            os._exit(1)

    return psutil.Process(pid)
