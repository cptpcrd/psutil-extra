# Type checkers don't like the wrapper names not existing.
# mypy: ignore-errors
# pytype: disable=module-attr
import resource
import sys
from typing import List, Optional, Tuple, Union, cast

import psutil

__version__ = "0.1.0"

if sys.platform.startswith("linux"):
    from . import _pslinux

    _psimpl = _pslinux
elif sys.platform.startswith("freebsd"):
    from . import _psfreebsd

    _psimpl = _psfreebsd
elif sys.platform.startswith("netbsd"):
    from . import _psnetbsd

    _psimpl = _psnetbsd
elif sys.platform.startswith("dragonfly"):
    from . import _psdragonfly

    _psimpl = _psdragonfly
elif sys.platform.startswith("darwin"):
    from . import _psmacosx

    _psimpl = _psmacosx
elif sys.platform.startswith("solaris"):
    from . import _pssolaris

    _psimpl = _pssolaris
else:
    _psimpl = None


def _get_pid(proc: Union[int, psutil.Process], *, check_running: bool = False) -> int:
    if isinstance(proc, int):
        return proc
    else:
        if check_running:
            if not proc.is_running():
                raise psutil.NoSuchProcess(proc.pid)

        return cast(int, proc.pid)


if sys.platform.startswith(("linux", "freebsd")):

    def proc_get_umask(proc: Union[int, psutil.Process]) -> int:
        """Get the umask of the given process.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.

        Returns:
            The given process's umask.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_get_umask(pid)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)


if sys.platform.startswith(("linux", "freebsd", "dragonfly", "darwin", "netbsd", "solaris")):

    def proc_getgroups(proc: Union[int, psutil.Process]) -> List[int]:
        """Get the supplementary group list for the given process.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.

        Returns:
            A list containing the given process's supplementary groups.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_getgroups(pid)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)


if sys.platform.startswith(("linux", "freebsd", "netbsd")):

    def proc_rlimit(
        proc: Union[int, psutil.Process], res: int, new_limits: Optional[Tuple[int, int]] = None
    ) -> Tuple[int, int]:
        """Identical to ``Process.rlimit()``, but is implemented for some platforms
        other than Linux.

        WARNING: This function may not be able to set the soft and hard resource limits
        in one operation. If it returns with an error, one or both of the limits may have
        been changed.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on. If a ``psutil.Process`` is given and ``new_limits`` is
                passed, this function preemptively checks ``Process.is_running()``.
            res: The resource (one of the ``resource.RLIMIT_*`` constants) to get/set.
            new_limits: If given and not ``None``, the new ``(soft, hard)`` resource
                limits to set.

        Returns:
            A tuple of the given process's ``(soft, hard)`` limits for the given
            resource (prior to setting the new limits).

        """

        pid = _get_pid(proc, check_running=(new_limits is not None))

        if new_limits is not None:
            soft, hard = new_limits

            if soft > hard:
                raise ValueError("current limit exceeds maximum limit")

            if soft < 0:
                soft = resource.RLIM_INFINITY
            if hard < 0:
                hard = resource.RLIM_INFINITY

            new_limits = (soft, hard)

        try:
            return _psimpl.proc_rlimit(pid, res, new_limits)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)


if sys.platform.startswith(("linux", "freebsd", "netbsd", "dragonfly")):

    def proc_getrlimit(proc: Union[int, psutil.Process], res: int) -> Tuple[int, int]:
        """A version of ``proc_rlimit()`` that only supports *getting* resource limits
        (but is implemented on more platforms).

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.
            res: The resource (one of the ``resource.RLIMIT_*`` constants) to get/set.

        Returns:
            A tuple of the given process's ``(soft, hard)`` limits for the given
            resource.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_getrlimit(pid, res)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)
