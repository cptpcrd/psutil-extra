import errno
import os
import sys

import psutil
import pytest

import psutil_extra

from .util import fork_proc

if sys.platform.startswith(("linux", "freebsd")):

    def test_get_umask() -> None:
        try:
            mask = psutil_extra.proc_get_umask(os.getpid())
        except OSError as ex:
            # Getting an ENOTSUP error is valid (occurs on Linux<4.7)
            if ex.errno == errno.ENOTSUP:
                return
            else:
                raise

        old_mask = os.umask(mask)
        try:
            assert old_mask == mask
        finally:
            os.umask(old_mask)

        assert psutil_extra.proc_get_umask(psutil.Process(os.getpid())) == mask

    def test_get_umask_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(proc)

    def test_getgroups() -> None:
        groups = psutil_extra.proc_getgroups(os.getpid())
        assert set(groups) == set(os.getgroups())

        assert set(psutil_extra.proc_getgroups(psutil.Process(os.getpid()))) == set(groups)

    def test_getgroups_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc)
