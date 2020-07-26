import os
import sys

import psutil_extra

if sys.platform.startswith(
    ("linux", "freebsd", "dragonfly", "darwin", "netbsd", "openbsd", "solaris")
):

    def test_cache() -> None:
        # This is a simple test. The cache is actually hard to test
        # because the details of which functions get speedups vary
        # between systems.

        pid = os.getpid()

        groups = psutil_extra.proc_getgroups(pid)
        pgid = psutil_extra.proc_getpgid(pid)
        sid = psutil_extra.proc_getsid(pid)

        with psutil_extra.oneshot_proc(pid):
            assert psutil_extra.proc_getgroups(pid) == groups
            assert psutil_extra.proc_getpgid(pid) == pgid
            assert psutil_extra.proc_getsid(pid) == sid
