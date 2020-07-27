import os
import resource
import sys

import psutil
import pytest

import psutil_extra
from psutil_extra._util import RESOURCE_NUMS

from .util import fork_proc

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

        with psutil_extra.oneshot_proc(os.getpid()):
            assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE) == limits
            assert psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE, limits) == limits

            assert (
                psutil_extra.proc_rlimit(psutil.Process(os.getpid()), resource.RLIMIT_NOFILE)
                == limits
            )
            assert (
                psutil_extra.proc_rlimit(
                    psutil.Process(os.getpid()), resource.RLIMIT_NOFILE, limits
                )
                == limits
            )

    def test_proc_rlimit_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(-1, resource.RLIMIT_NOFILE)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_rlimit(-1, resource.RLIMIT_NOFILE)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(proc.pid, resource.RLIMIT_NOFILE)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(
                proc.pid, resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE)
            )

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(proc, resource.RLIMIT_NOFILE)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_rlimit(
                proc, resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE)
            )

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_rlimit(proc.pid, resource.RLIMIT_NOFILE)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_rlimit(
                    proc.pid, resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE)
                )

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_rlimit(proc, resource.RLIMIT_NOFILE)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_rlimit(
                    proc, resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE)
                )

    def test_proc_rlimit_error() -> None:
        with pytest.raises(ValueError, match=r"^current limit exceeds maximum limit$"):
            psutil_extra.proc_rlimit(os.getpid(), resource.RLIMIT_NOFILE, (1, 0))

        with pytest.raises(ValueError, match=r"^invalid resource specified$"):
            psutil_extra.proc_rlimit(os.getpid(), max(RESOURCE_NUMS) + 1)


if sys.platform.startswith(("linux", "freebsd", "netbsd", "dragonfly")):

    def test_proc_getrlimit() -> None:
        assert psutil_extra.proc_getrlimit(
            os.getpid(), resource.RLIMIT_NOFILE
        ) == resource.getrlimit(resource.RLIMIT_NOFILE)

        assert psutil_extra.proc_getrlimit(
            psutil.Process(os.getpid()), resource.RLIMIT_NOFILE
        ) == resource.getrlimit(resource.RLIMIT_NOFILE)

        with psutil_extra.oneshot_proc(os.getpid()):
            assert psutil_extra.proc_getrlimit(
                os.getpid(), resource.RLIMIT_NOFILE
            ) == resource.getrlimit(resource.RLIMIT_NOFILE)

            assert psutil_extra.proc_getrlimit(
                psutil.Process(os.getpid()), resource.RLIMIT_NOFILE
            ) == resource.getrlimit(resource.RLIMIT_NOFILE)

    def test_proc_getrlimit_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getrlimit(-1, resource.RLIMIT_NOFILE)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getrlimit(-1, resource.RLIMIT_NOFILE)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getrlimit(proc.pid, resource.RLIMIT_NOFILE)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getrlimit(proc, resource.RLIMIT_NOFILE)

        with psutil_extra.oneshot_proc(proc.pid):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getrlimit(proc.pid, resource.RLIMIT_NOFILE)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getrlimit(proc, resource.RLIMIT_NOFILE)

    def test_proc_getrlimit_error() -> None:
        with pytest.raises(ValueError, match=r"^invalid resource specified$"):
            psutil_extra.proc_getrlimit(os.getpid(), max(RESOURCE_NUMS) + 1)
