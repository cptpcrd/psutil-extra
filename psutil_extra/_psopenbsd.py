# pylint: disable=too-few-public-methods
import ctypes
from typing import List, cast

from . import _bsd, _cache, _psposix, _util
from ._util import ProcessSignalMasks

CTL_KERN = 1

KERN_PROC = 66
KERN_PROC_PID = 1

KI_NGROUPS = 16
KI_MAXCOMLEN = 24
KI_WMESGLEN = 8
KI_MAXLOGNAME = 32
KI_MAXEMULLEN = 16


class KinfoProc(ctypes.Structure):
    _fields_ = [
        ("p_forw", ctypes.c_uint64),
        ("p_back", ctypes.c_uint64),
        ("p_paddr", ctypes.c_uint64),
        ("p_addr", ctypes.c_uint64),
        ("p_fd", ctypes.c_uint64),
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
        ("p_siglist", ctypes.c_int32),
        ("p_sigmask", ctypes.c_uint32),
        ("p_sigignore", ctypes.c_uint32),
        ("p_sigcatch", ctypes.c_uint32),
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
        ("p_ustart_sec", ctypes.c_uint64),
        ("p_ustart_usec", ctypes.c_uint64),
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
        ("p_uctime_sec", ctypes.c_uint32),
        ("p_uctime_usec", ctypes.c_uint32),
        ("p_psflags", ctypes.c_int32),
        ("p_spare", ctypes.c_int32),
        ("p_svuid", ctypes.c_uint32),
        ("p_svgid", ctypes.c_uint32),
        ("p_emul", (ctypes.c_char * KI_MAXEMULLEN)),
        ("p_rlim_rss_cur", ctypes.c_uint64),
        ("p_cpuid", ctypes.c_uint64),
        ("p_vm_map_size", ctypes.c_uint64),
        ("p_tid", ctypes.c_int32),
        ("p_rtableid", ctypes.c_uint32),
        ("p_pledge", ctypes.c_uint64),
    ]

    def get_groups(self) -> List[int]:
        return list(self.p_groups[: self.p_ngroups])


@_cache.CachedByPid
def _get_kinfo_proc(pid: int) -> KinfoProc:
    if pid <= 0:
        raise ProcessLookupError

    proc_info = KinfoProc()

    length = _bsd.sysctl([CTL_KERN, KERN_PROC, KERN_PROC_PID, pid], None, proc_info)

    if length == 0:
        raise ProcessLookupError

    return proc_info


def proc_getgroups(pid: int) -> List[int]:
    return _get_kinfo_proc(pid).get_groups()


def proc_get_sigmasks(pid: int) -> ProcessSignalMasks:
    kinfo = _get_kinfo_proc(pid)

    return ProcessSignalMasks(
        pending=_util.expand_sig_bitmask(kinfo.p_siglist),
        blocked=_util.expand_sig_bitmask(kinfo.p_sigmask),
        ignored=_util.expand_sig_bitmask(kinfo.p_sigignore),
        caught=_util.expand_sig_bitmask(kinfo.p_sigcatch),
    )


def proc_getpgid(pid: int) -> int:
    if _cache.is_enabled(pid):
        # We're in a oneshot_proc(); retrieve extra information
        return cast(int, _get_kinfo_proc(pid).p__pgid)
    else:
        try:
            return _psposix.proc_getpgid(pid)
        except PermissionError:
            return cast(int, _get_kinfo_proc(pid).p__pgid)


def proc_getsid(pid: int) -> int:
    if _cache.is_enabled(pid):
        # We're in a oneshot_proc(); retrieve extra information
        return cast(int, _get_kinfo_proc(pid).p_sid)
    else:
        try:
            return _psposix.proc_getsid(pid)
        except PermissionError:
            return cast(int, _get_kinfo_proc(pid).p_sid)
