import os
import resource
import sys

import psutil_extra

if sys.platform.startswith(("linux", "freebsd", "netbsd")):

    def test_proc_rlimit() -> None:
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)

        assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE) == limits
        assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE, limits) == limits


if sys.platform.startswith(("linux", "freebsd", "netbsd", "dragonfly")):

    def test_proc_getrlimit() -> None:
        assert psutil_extra.proc_getrlimit(
            os.getpid(), resource.RLIMIT_NOFILE
        ) == resource.getrlimit(resource.RLIMIT_NOFILE)
