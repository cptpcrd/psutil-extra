import os
from typing import Callable

import psutil


def fork_proc(child_func: Callable[[], None]) -> psutil.Process:
    pid = os.fork()
    if pid == 0:
        try:
            child_func()
        except SystemExit as ex:
            os._exit(ex.code)  # pylint: disable=protected-access
        finally:
            # Make sure we exit somehow
            os._exit(1)  # pylint: disable=protected-access

    return psutil.Process(pid)
