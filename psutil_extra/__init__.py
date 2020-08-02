# Type checkers don't like the wrapper names not existing.
# mypy: ignore-errors
# pytype: disable=module-attr
import errno
import resource
import sys
from typing import Any, ContextManager, Dict, Iterable, List, Optional, Tuple, Union, cast

import psutil

from . import _cache

__version__ = "0.2.0"

if sys.platform.startswith("linux"):
    from . import _pslinux

    _psimpl = _pslinux
elif sys.platform.startswith("freebsd"):
    from . import _psfreebsd

    _psimpl = _psfreebsd
elif sys.platform.startswith("netbsd"):
    from . import _psnetbsd

    _psimpl = _psnetbsd
elif sys.platform.startswith("openbsd"):
    from . import _psopenbsd

    _psimpl = _psopenbsd
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


def oneshot_proc(pid: int) -> ContextManager[None]:
    """Similar to ``psutil.Process.oneshot()``, enables caching of values that can be
    retrieved by the same method.

    WARNING: This function differs from ``psutil.Process.oneshot()`` in two important ways:

    - The process information cache is thread-local. This avoids concurrent modification issues.
    - The caching is done by PID, not by ``psutil.Process`` instance, and as a result the cache
      will be used regardless of whether a ``psutil.Process`` or an integer PID is passed to the
      underlying function. For example, if ``proc_getgroups(1)`` and then
      ``proc_getgroups(psutil.Process(1))`` are called inside a ``with oneshot_proc(1)`` block,
      ``psutil_extra`` will use the cached information for the second call.

    Args:
        pid: The PID of the process for which information should be cached.

    Yields:
        ``None`` (a per-process cache is enabled while inside the context manager)

    """

    if not isinstance(pid, int):
        raise TypeError("oneshot_proc() pid must be an integer")

    return _cache.oneshot_proc(pid)


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


if sys.platform.startswith(
    ("linux", "darwin", "freebsd", "openbsd", "netbsd", "dragonfly", "solaris")
):

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


if sys.platform.startswith(("linux", "darwin", "freebsd", "openbsd", "netbsd")):
    ProcessSignalMasks = _psimpl.ProcessSignalMasks  # pytype: disable=attribute-error

    def proc_get_sigmasks(  # pytype: disable=invalid-annotation
        proc: Union[int, psutil.Process]
    ) -> ProcessSignalMasks:
        """Get the signal masks of the given process. Returns a dataclass containing
        several fields:

        - ``pending`` (not on macOS): The set of pending signals for the process.
        - ``blocked`` (not on macOS): The set of signals that the process has blocked.
        - ``ignored``: The set of signals that the process has ignored.
        - ``caught``: The set of signals that the process has registered signal
          handlers for.
        - ``process_pending`` (Linux): The set of pending signals for the entire process,
          not just the specified thread.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.

        Returns:
            A dataclass containing the fields listed above.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_get_sigmasks(pid)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)


if sys.platform.startswith(
    ("linux", "darwin", "freebsd", "openbsd", "netbsd", "dragonfly", "solaris")
):

    def proc_getpgid(proc: Union[int, psutil.Process]) -> int:
        """Get the process group ID of the given process.

        On platforms where ``os.getpgid()`` returns EPERM for processes in other sessions,
        this function may still be able to get the process group ID for these processes.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.

        Returns:
            The process group ID of the given process.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_getpgid(pid)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)

    def proc_getsid(proc: Union[int, psutil.Process]) -> int:
        """Get the sessopm ID of the given process.

        On platforms where ``os.getsid()`` returns EPERM for processes in other sessions,
        this function may still be able to get the session ID for these processes.

        Args:
            proc: Either an integer PID or a ``psutil.Process`` specifying the process
                to operate on.

        Returns:
            The session ID of the given process.

        """

        pid = _get_pid(proc)

        try:
            return _psimpl.proc_getsid(pid)
        except ProcessLookupError:
            raise psutil.NoSuchProcess(pid)
        except PermissionError:
            raise psutil.AccessDenied(pid)


_PROC_DICT_FUNCS = {
    name: globals()[func_name]
    for (name, func_name) in [
        ("umask", "proc_get_umask"),
        ("groups", "proc_getgroups"),
        ("sigmasks", "proc_get_sigmasks"),
        ("pgid", "proc_getpgid"),
        ("sid", "proc_getsid"),
    ]
    if func_name in globals()
}


def proc_as_dict(
    proc: Union[int, psutil.Process], *, attrs: Optional[Iterable[str]] = None, ad_value: Any = None
) -> Dict[str, Any]:
    pid = _get_pid(proc)

    res = {}

    if attrs is None:
        attrs = _PROC_DICT_FUNCS.keys()

    with oneshot_proc(pid):
        for name in attrs:
            if not isinstance(name, str):
                raise TypeError("invalid attr type {!r}".format(type(name)))

            if name in _PROC_DICT_FUNCS:
                try:
                    res[name] = _PROC_DICT_FUNCS[name](pid)  # pytype: disable=not-callable
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    res[name] = ad_value
                except OSError as ex:
                    if ex.errno == errno.ENOTSUP:
                        res[name] = ad_value
                    else:
                        raise
            else:
                raise ValueError("invalid attr name {!r}".format(name))

    return res
