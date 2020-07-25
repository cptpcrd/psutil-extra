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


if sys.platform.startswith(("linux", "freebsd", "dragonfly", "darwin", "netbsd", "solaris")):

    def test_getgroups() -> None:
        groups = set(psutil_extra.proc_getgroups(os.getpid()))
        groups_alt = set(psutil_extra.proc_getgroups(psutil.Process(os.getpid())))

        # Check for internal consistency when using PIDs vs psutil.Processes
        assert set(groups) == set(groups_alt)

        cur_groups = os.getgroups()
        if sys.platform.startswith(("freebsd", "darwin", "netbsd")):
            # These platforms may truncate the group list.

            if cur_groups:
                # We have at least one supplementary group.
                # Make sure that the list we got isn't empty
                assert groups

                # Also make sure it doesn't contain any "extra" groups
                assert set(groups) <= set(cur_groups)
            else:
                # No supplementary groups; make sure the list we
                # got confirms that.
                assert not groups
        else:
            # Linux shouldn't truncate the group list.
            assert set(groups) == set(cur_groups)

    def test_getgroups_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc)
