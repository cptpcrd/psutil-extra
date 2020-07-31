# pylint: disable=too-few-public-methods
import ctypes
import errno
from typing import List, Optional, Tuple, cast

from . import _bsd, _cache, _psposix, _util
from ._util import ProcessSignalMasks

CTL_KERN = 1
CTL_PROC = 10

PROC_PID_LIMIT = 2
PROC_PID_LIMIT_TYPE_SOFT = 1
PROC_PID_LIMIT_TYPE_HARD = 2

KERN_PROC2 = 47
KERN_PROC_PID = 1

KI_NGROUPS = 16
KI_MAXCOMLEN = 24
KI_WMESGLEN = 8
KI_MAXLOGNAME = 24
KI_MAXEMULLEN = 16

rlim_t = ctypes.c_uint64  # pylint: disable=invalid-name


def _proc_rlimit_getset(pid: int, res: int, new_limit: Optional[int], hard: bool) -> int:
    new_limit_raw = ctypes.byref(rlim_t(new_limit)) if new_limit is not None else None
    old_limit = rlim_t(0)

    _bsd.sysctl(  # pytype: disable=wrong-arg-types
        [
            CTL_PROC,
            pid,
            PROC_PID_LIMIT,
            res + 1,
            (PROC_PID_LIMIT_TYPE_HARD if hard else PROC_PID_LIMIT_TYPE_SOFT),
        ],
        new_limit_raw,  # type: ignore
        old_limit,  # type: ignore
    )

    return old_limit.value


def proc_rlimit(
    pid: int, res: int, new_limits: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    if pid <= 0:
        raise ProcessLookupError

    _util.check_rlimit_resource(res)

    new_soft: Optional[int]
    new_hard: Optional[int]
    if new_limits is not None:
        new_soft = new_limits[0]
        new_hard = new_limits[1]
    else:
        new_soft = None
        new_hard = None

    old_soft: Optional[int]
    try:
        old_soft = _proc_rlimit_getset(pid, res, new_soft, False)
    except OSError as ex:
        if ex.errno == errno.EINVAL:
            old_soft = None
        else:
            raise

    old_hard = _proc_rlimit_getset(pid, res, new_hard, True)

    if old_soft is None:
        old_soft = _proc_rlimit_getset(pid, res, new_soft, False)

    return old_soft, old_hard


proc_getrlimit = proc_rlimit


class KiSigset(ctypes.Structure):
    _fields_ = [
        ("bits", (ctypes.c_uint32 * 4)),
    ]

    def pack(self) -> int:
        # https://github.com/IIJ-NetBSD/netbsd-src/blob/e4505e0610ceb1b2db8e2a9ed607b4bfa076aa2f/sys/sys/sigtypes.h

        return cast(int, self.bits[0])


class KinfoProc2(ctypes.Structure):
    _fields_ = [
        ("p_forw", ctypes.c_uint64),
        ("p_back", ctypes.c_uint64),
        ("p_paddr", ctypes.c_uint64),
        ("p_addr", ctypes.c_uint64),
        ("p_fd", ctypes.c_uint64),
        ("p_cwdi", ctypes.c_uint64),
        ("p_stats", ctypes.c_uint64),
        ("p_limit", ctypes.c_uint64),
        ("p_vmspace", ctypes.c_uint64),
        ("p_sigacts", ctypes.c_uint64),
        ("p_sess", ctypes.c_uint64),
        ("p_tsess", ctypes.c_uint64),
        ("p_ru", ctypes.c_uint64),
        ("p_eflag", ctypes.c_int32),
        ("p_exitsig", ctypes.c_int32),
        ("p_flag", ctypes.c_int32),
        ("p_pid", ctypes.c_int32),
        ("p_ppid", ctypes.c_int32),
        ("p_sid", ctypes.c_int32),
        ("p__pgid", ctypes.c_int32),
        ("p_tpgid", ctypes.c_int32),
        ("p_uid", ctypes.c_uint32),
        ("p_ruid", ctypes.c_uint32),
        ("p_gid", ctypes.c_uint32),
        ("p_rgid", ctypes.c_uint32),
        ("p_groups", (ctypes.c_uint32 * KI_NGROUPS)),
        ("p_ngroups", ctypes.c_int16),
        ("p_jobc", ctypes.c_int16),
        ("p_tdev", ctypes.c_uint32),
        ("p_estcpu", ctypes.c_uint32),
        ("p_rtime_sec", ctypes.c_uint32),
        ("p_rtime_usec", ctypes.c_uint32),
        ("p_cpticks", ctypes.c_int32),
        ("p_cptcpu", ctypes.c_uint32),
        ("p_swtime", ctypes.c_uint32),
        ("p_slptime", ctypes.c_uint32),
        ("p_schedflags", ctypes.c_int32),
        ("p_uticks", ctypes.c_uint64),
        ("p_sticks", ctypes.c_uint64),
        ("p_iticks", ctypes.c_uint64),
        ("p_tracep", ctypes.c_uint64),
        ("p_traceflag", ctypes.c_int32),
        ("p_holdcnt", ctypes.c_int32),
        ("p_siglist", KiSigset),
        ("p_sigmask", KiSigset),
        ("p_sigignore", KiSigset),
        ("p_sigcatch", KiSigset),
        ("p_stat", ctypes.c_int8),
        ("p_priority", ctypes.c_uint8),
        ("p_usrpri", ctypes.c_uint8),
        ("p_nice", ctypes.c_uint8),
        ("p_xstat", ctypes.c_uint16),
        ("p_acflag", ctypes.c_uint16),
        ("p_comm", (ctypes.c_char * KI_MAXCOMLEN)),
        ("p_wmesg", (ctypes.c_char * KI_WMESGLEN)),
        ("p_wchan", ctypes.c_uint64),
        ("p_login", (ctypes.c_char * KI_MAXLOGNAME)),
        ("p_vm_rssize", ctypes.c_int32),
        ("p_vm_tsize", ctypes.c_int32),
        ("p_vm_dsize", ctypes.c_int32),
        ("p_vm_ssize", ctypes.c_int32),
        ("p_uvalid", ctypes.c_int64),
        ("p_ustart_sec", ctypes.c_uint32),
        ("p_ustart_usec", ctypes.c_uint32),
        ("p_uutime_sec", ctypes.c_uint32),
        ("p_uutime_usec", ctypes.c_uint32),
        ("p_ustime_sec", ctypes.c_uint32),
        ("p_ustime_usec", ctypes.c_uint32),
        ("p_uru_maxrss", ctypes.c_uint64),
        ("p_uru_ixrss", ctypes.c_uint64),
        ("p_uru_idrss", ctypes.c_uint64),
        ("p_uru_isrss", ctypes.c_uint64),
        ("p_uru_minflt", ctypes.c_uint64),
        ("p_uru_majflt", ctypes.c_uint64),
        ("p_uru_nswap", ctypes.c_uint64),
        ("p_uru_inblock", ctypes.c_uint64),
        ("p_uru_oublock", ctypes.c_uint64),
        ("p_uru_msgsnd", ctypes.c_uint64),
        ("p_uru_msgrcv", ctypes.c_uint64),
        ("p_uru_nsignals", ctypes.c_uint64),
        ("p_uru_nvcsw", ctypes.c_uint64),
        ("p_uru_nivcsw", ctypes.c_uint64),
        ("p_uctime_sec", ctypes.c_uint32),
        ("p_uctime_usec", ctypes.c_uint32),
        ("p_cpuid", ctypes.c_uint64),
        ("p_realflag", ctypes.c_uint64),
        ("p_nlwps", ctypes.c_uint64),
        ("p_nrlwps", ctypes.c_uint64),
        ("p_realstat", ctypes.c_uint64),
        ("p_svuid", ctypes.c_uint64),
        ("p_svgid", ctypes.c_uint64),
        ("p_ename", (ctypes.c_char * KI_MAXEMULLEN)),
        ("p_vm_vsize", ctypes.c_int64),
        ("p_vm_msize", ctypes.c_int64),
    ]

    def get_groups(self) -> List[int]:
        return list(self.p_groups[: self.p_ngroups])


@_cache.CachedByPid
def _get_kinfo_proc2(pid: int) -> KinfoProc2:
    if pid <= 0:
        raise ProcessLookupError

    proc_info = KinfoProc2()

    length = _bsd.sysctl([CTL_KERN, KERN_PROC2, KERN_PROC_PID, pid], None, proc_info)

    if length == 0:
        raise ProcessLookupError

    return proc_info


def proc_getgroups(pid: int) -> List[int]:
    return _get_kinfo_proc2(pid).get_groups()


def proc_get_sigmasks(pid: int) -> ProcessSignalMasks:
    kinfo = _get_kinfo_proc2(pid)

    return ProcessSignalMasks(
        pending=_util.expand_sig_bitmask(kinfo.p_siglist.pack()),
        blocked=_util.expand_sig_bitmask(kinfo.p_sigmask.pack()),
        ignored=_util.expand_sig_bitmask(kinfo.p_sigignore.pack()),
        caught=_util.expand_sig_bitmask(kinfo.p_sigcatch.pack()),
    )


def proc_getpgid(pid: int) -> int:
    if _cache.is_enabled(pid):
        # We're in a oneshot_proc(); retrieve extra information
        return cast(int, _get_kinfo_proc2(pid).p__pgid)
    else:
        return _psposix.proc_getpgid(pid)


def proc_getsid(pid: int) -> int:
    if _cache.is_enabled(pid):
        # We're in a oneshot_proc(); retrieve extra information
        return cast(int, _get_kinfo_proc2(pid).p_sid)
    else:
        return _psposix.proc_getsid(pid)
