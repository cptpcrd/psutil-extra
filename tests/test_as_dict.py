import psutil
import pytest

import psutil_extra


def test_as_dict() -> None:
    proc = psutil.Process()
    pid = proc.pid

    info = psutil_extra.proc_as_dict(pid)
    assert info == psutil_extra.proc_as_dict(proc)

    if hasattr(psutil_extra, "proc_get_umask"):
        assert info["umask"] == psutil_extra.proc_get_umask(pid)
        assert info["umask"] == psutil_extra.proc_as_dict(pid)["umask"]

    if hasattr(psutil_extra, "proc_getgroups"):
        assert info["groups"] == psutil_extra.proc_getgroups(pid)
        assert info["groups"] == psutil_extra.proc_as_dict(pid)["groups"]

    if hasattr(psutil_extra, "proc_get_sigmasks"):
        assert info["sigmasks"] == psutil_extra.proc_get_sigmasks(pid)
        assert info["sigmasks"] == psutil_extra.proc_as_dict(pid)["sigmasks"]

    if hasattr(psutil_extra, "proc_getpgid"):
        assert info["pgid"] == psutil_extra.proc_getpgid(pid)
        assert info["pgid"] == psutil_extra.proc_as_dict(pid)["pgid"]

    if hasattr(psutil_extra, "proc_getsid"):
        assert info["sid"] == psutil_extra.proc_getsid(pid)
        assert info["sid"] == psutil_extra.proc_as_dict(pid)["sid"]


def test_as_dict_error() -> None:
    with pytest.raises(psutil.NoSuchProcess):
        psutil_extra.proc_as_dict(-1)

    with pytest.raises(TypeError, match="^invalid attr type <class 'int'>$"):
        psutil_extra.proc_as_dict(1, attrs=[1])  # type: ignore

    with pytest.raises(ValueError, match="^invalid attr name 'BAD_ATTR'$"):
        psutil_extra.proc_as_dict(1, attrs=["BAD_ATTR"])
