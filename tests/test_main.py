import errno
import os
import sys

import psutil
import pytest

import psutil_extra

from .util import fork_proc


def test_oneshot_proc_error() -> None:
    with pytest.raises(TypeError, match=r"^oneshot_proc\(\) pid must be an integer$"):
        with psutil_extra.oneshot_proc(psutil.Process()):
            pass

    with pytest.raises(TypeError, match=r"^oneshot_proc\(\) pid must be an integer$"):
        with psutil_extra.oneshot_proc(""):  # type: ignore
            pass


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

        with psutil_extra.oneshot_proc(os.getpid()):
            assert mask == psutil_extra.proc_get_umask(os.getpid())

            assert mask == psutil_extra.proc_get_umask(psutil.Process(os.getpid()))

    def test_get_umask_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(-1)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_get_umask(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_get_umask(proc)

        with psutil_extra.oneshot_proc(proc.pid):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_get_umask(proc.pid)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_get_umask(proc)


if sys.platform.startswith(("linux", "darwin", "freebsd", "netbsd", "dragonfly", "solaris")):

    def test_getgroups() -> None:
        groups = psutil_extra.proc_getgroups(os.getpid())
        groups_alt = psutil_extra.proc_getgroups(psutil.Process(os.getpid()))

        # Check for internal consistency when using PIDs vs psutil.Processes
        assert set(groups) == set(groups_alt)

        # And when using oneshot_proc()
        with psutil_extra.oneshot_proc(os.getpid()):
            assert set(groups) == set(psutil_extra.proc_getgroups(os.getpid()))
            assert set(groups) == set(psutil_extra.proc_getgroups(psutil.Process(os.getpid())))

        cur_groups = os.getgroups()

        if sys.platform.startswith("darwin"):
            # In macOS 10.5, Apple decided to change the behavior of getgroups() to make
            # it non-POSIX compliant and not an accurate reflection of the process's
            # supplementary group list. <sigh>
            assert set(groups) <= set(cur_groups)
        else:
            # Check that the group list matches
            assert set(groups) == set(cur_groups)

    def test_getgroups_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(-1)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getgroups(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getgroups(proc)

        with psutil_extra.oneshot_proc(proc.pid):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getgroups(proc.pid)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getgroups(proc)


if sys.platform.startswith(
    ("linux", "darwin", "freebsd", "openbsd", "netbsd", "dragonfly", "solaris")
):

    def test_getpgid() -> None:
        assert psutil_extra.proc_getpgid(os.getpid()) == os.getpgrp()

        with psutil_extra.oneshot_proc(os.getpid()):
            assert psutil_extra.proc_getpgid(os.getpid()) == os.getpgrp()

        assert psutil_extra.proc_getpgid(1) == 1

        with psutil_extra.oneshot_proc(1):
            assert psutil_extra.proc_getpgid(1) == 1

    def test_getpgid_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getpgid(-1)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getpgid(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getpgid(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getpgid(proc)

        with psutil_extra.oneshot_proc(proc.pid):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getpgid(proc.pid)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getpgid(proc)

    def test_getsid() -> None:
        assert psutil_extra.proc_getsid(os.getpid()) == os.getsid(os.getpid())

        with psutil_extra.oneshot_proc(os.getpid()):
            assert psutil_extra.proc_getsid(os.getpid()) == os.getsid(os.getpid())

        assert psutil_extra.proc_getsid(1) == 1

        with psutil_extra.oneshot_proc(1):
            assert psutil_extra.proc_getsid(1) == 1

        with psutil_extra.oneshot_proc(1):
            assert psutil_extra.proc_getsid(1) == 1

            with psutil_extra.oneshot_proc(1):
                assert psutil_extra.proc_getsid(1) == 1

            assert psutil_extra.proc_getsid(1) == 1

    def test_getsid_no_proc() -> None:
        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getsid(-1)

        with psutil_extra.oneshot_proc(-1):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getsid(-1)

        proc = fork_proc(lambda: sys.exit(0))
        proc.wait(timeout=1)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getsid(proc.pid)

        with pytest.raises(psutil.NoSuchProcess):
            psutil_extra.proc_getsid(proc)

        with psutil_extra.oneshot_proc(proc.pid):
            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getsid(proc.pid)

            with pytest.raises(psutil.NoSuchProcess):
                psutil_extra.proc_getsid(proc)

        with psutil_extra.oneshot_proc(proc.pid):
            with psutil_extra.oneshot_proc(proc.pid):
                with pytest.raises(psutil.NoSuchProcess):
                    psutil_extra.proc_getsid(proc.pid)
