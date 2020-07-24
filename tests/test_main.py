import os
import sys

import psutil
import pytest

import psutil_extra

if sys.platform.startswith(("linux", "freebsd")):

    def test_get_umask() -> None:
        mask = psutil_extra.proc_get_umask(os.getpid())

        old_mask = os.umask(mask)
        try:
            assert old_mask == mask
        finally:
            os.umask(old_mask)

        assert psutil_extra.proc_get_umask(psutil.Process(os.getpid())) == mask

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(-1)

    def test_getgroups() -> None:
        groups = psutil_extra.proc_getgroups(os.getpid())
        assert set(groups) == set(os.getgroups())

        assert set(psutil_extra.proc_getgroups(psutil.Process(os.getpid()))) == set(groups)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(-1)
