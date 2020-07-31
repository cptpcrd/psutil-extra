import errno
from typing import Optional

import psutil
import pytest

import psutil_extra


def test_as_dict() -> None:
    proc = psutil.Process()
    pid = proc.pid

    info = psutil_extra.proc_as_dict(pid)
    assert info == psutil_extra.proc_as_dict(proc)

    if hasattr(psutil_extra, "proc_get_umask"):
        umask: Optional[int]

        try:
            umask = psutil_extra.proc_get_umask(pid)
        except OSError as ex:
            if ex.errno == errno.ENOTSUP:
                umask = None
            else:
                raise

        assert info["umask"] == umask
        assert psutil_extra.proc_as_dict(pid, attrs=["umask"]) == {"umask": info["umask"]}

    if hasattr(psutil_extra, "proc_getgroups"):
        assert info["groups"] == psutil_extra.proc_getgroups(pid)
        assert psutil_extra.proc_as_dict(pid, attrs=["groups"]) == {"groups": info["groups"]}

    if hasattr(psutil_extra, "proc_get_sigmasks"):
        assert info["sigmasks"] == psutil_extra.proc_get_sigmasks(pid)
        assert psutil_extra.proc_as_dict(pid, attrs=["sigmasks"]) == {"sigmasks": info["sigmasks"]}

    if hasattr(psutil_extra, "proc_getpgid"):
        assert info["pgid"] == psutil_extra.proc_getpgid(pid)
        assert psutil_extra.proc_as_dict(pid, attrs=["pgid"]) == {"pgid": info["pgid"]}

    if hasattr(psutil_extra, "proc_getsid"):
        assert info["sid"] == psutil_extra.proc_getsid(pid)
        assert psutil_extra.proc_as_dict(pid, attrs=["sid"]) == {"sid": info["sid"]}


def test_as_dict_error() -> None:
    with pytest.raises(psutil.NoSuchProcess):
        psutil_extra.proc_as_dict(-1)

    with pytest.raises(TypeError, match="^invalid attr type <class 'int'>$"):
        psutil_extra.proc_as_dict(1, attrs=[1])  # type: ignore

    with pytest.raises(ValueError, match="^invalid attr name 'BAD_ATTR'$"):
        psutil_extra.proc_as_dict(1, attrs=["BAD_ATTR"])
