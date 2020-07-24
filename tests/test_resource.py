import os
import resource
import sys

import psutil
import pytest

import psutil_extra

if sys.platform.startswith(("linux", "freebsd", "netbsd")):

    def test_proc_rlimit() -> None:
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)

        assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE) == limits
        assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE, limits) == limits

        assert (
            psutil_extra.proc_rlimit(psutil.Process(os.getpid()), resource.RLIMIT_NOFILE) == limits
        )
        assert (
            psutil_extra.proc_rlimit(psutil.Process(os.getpid()), resource.RLIMIT_NOFILE, limits)
            == limits
        )

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(-1, resource.RLIMIT_NOFILE)


if sys.platform.startswith(("linux", "freebsd", "netbsd", "dragonfly")):

    def test_proc_getrlimit() -> None:
        assert psutil_extra.proc_getrlimit(
            os.getpid(), resource.RLIMIT_NOFILE
        ) == resource.getrlimit(resource.RLIMIT_NOFILE)

        assert psutil_extra.proc_getrlimit(
            psutil.Process(os.getpid()), resource.RLIMIT_NOFILE
        ) == resource.getrlimit(resource.RLIMIT_NOFILE)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getrlimit(-1, resource.RLIMIT_NOFILE)
