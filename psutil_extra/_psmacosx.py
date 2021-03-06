# pylint: disable=invalid-name,too-few-public-methods
import ctypes
import dataclasses
from typing import List, Set, cast

from . import _cache, _psposix, _util
from ._bsd import sysctl
from ._ffi import gid_t, pid_t, uid_t

WMESGLEN = 7
NGROUPS = 16
COMPAT_MAXLOGNAME = 12
MAXCOMLEN = 16

CTL_KERN = 1
KERN_PROC = 14
KERN_PROC_PID = 1

caddr_t = ctypes.c_char_p
segsz_t = ctypes.c_int32
dev_t = ctypes.c_int32
fixpt_t = ctypes.c_uint32
u_quad_t = ctypes.c_uint64
time_t = ctypes.c_long
suseconds_t = ctypes.c_int32
sigset_t = ctypes.c_uint32


@dataclasses.dataclass
class ProcessSignalMasks:
    ignored: Set[int]
    caught: Set[int]


class Timeval(ctypes.Structure):
    _fields_ = [
        ("tv_sec", time_t),
        ("tv_usec", suseconds_t),
    ]


class ITimerval(ctypes.Structure):
    _fields_ = [
        ("it_interval", Timeval),
        ("it_value", Timeval),
    ]


class ExternProcPunSt1(ctypes.Structure):
    _fields_ = [
        ("p_forw", ctypes.c_void_p),
        ("p_back", ctypes.c_void_p),
    ]


class ExternProcPun(ctypes.Union):
    _fields_ = [
        ("p_st1", ExternProcPunSt1),
        ("p_startime", Timeval),
    ]


class ExternProc(ctypes.Structure):
    _fields_ = [
        ("p_un", ExternProcPun),
        ("p_vmspace", ctypes.c_void_p),
        ("p_sigacts", ctypes.c_void_p),
        ("p_flag", ctypes.c_int),
        ("p_stat", ctypes.c_char),
        ("p_pid", pid_t),
        ("p_oppid", pid_t),
        ("p_dupfd", ctypes.c_int),
        ("user_stack", caddr_t),
        ("exit_thread", ctypes.c_void_p),
        ("p_debugger", ctypes.c_int),
        ("sigwait", ctypes.c_bool),
        ("p_estcpu", ctypes.c_uint),
        ("p_cpticks", ctypes.c_int),
        ("p_pctcpu", fixpt_t),
        ("p_wchan", ctypes.c_void_p),
        ("p_wmesg", ctypes.c_char_p),
        ("p_swtime", ctypes.c_uint),
        ("p_slptime", ctypes.c_uint),
        ("p_realtimer", ITimerval),
        ("p_rtime", Timeval),
        ("p_uticks", u_quad_t),
        ("p_sticks", u_quad_t),
        ("p_iticks", u_quad_t),
        ("p_traceflag", ctypes.c_int),
        ("p_tracep", ctypes.c_void_p),
        ("p_siglist", ctypes.c_int),
        ("p_textvp", ctypes.c_void_p),
        ("p_holdcnt", ctypes.c_int),
        ("p_sigmask", sigset_t),
        ("p_sigignore", sigset_t),
        ("p_sigcatch", sigset_t),
        ("p_priority", ctypes.c_ubyte),
        ("p_usrpri", ctypes.c_ubyte),
        ("p_nice", ctypes.c_char),
        ("p_comm", (ctypes.c_char * (MAXCOMLEN + 1))),
        ("p_pgrp", ctypes.c_void_p),
        ("p_addr", ctypes.c_void_p),
        ("p_xstat", ctypes.c_ushort),
        ("p_acflag", ctypes.c_ushort),
        ("p_ru", ctypes.c_void_p),
    ]


class Pcred(ctypes.Structure):
    _fields_ = [
        ("pc_lock", (ctypes.c_char * 72)),
        ("pc_ucred", ctypes.c_void_p),
        ("p_ruid", uid_t),
        ("p_svuid", uid_t),
        ("p_rgid", gid_t),
        ("p_svgid", gid_t),
        ("p_refcnt", ctypes.c_int),
    ]


class Ucred(ctypes.Structure):
    _fields_ = [
        ("cr_ref", ctypes.c_int32),
        ("cr_uid", uid_t),
        ("cr_ngroups", ctypes.c_short),
        ("cr_groups", (gid_t * NGROUPS)),
    ]


class Vmspace(ctypes.Structure):
    _fields_ = [
        ("vm_refcnt", ctypes.c_int),
        ("vm_shm", caddr_t),
        ("vm_rssize", segsz_t),
        ("vm_swrss", segsz_t),
        ("vm_tsize", segsz_t),
        ("vm_dsize", segsz_t),
        ("vm_ssize", segsz_t),
        ("vm_taddr", caddr_t),
        ("vm_daddr", caddr_t),
        ("vm_maxsaddr", caddr_t),
    ]


class Eproc(ctypes.Structure):
    _fields_ = [
        ("e_paddr", ctypes.c_void_p),
        ("e_sess", ctypes.c_void_p),
        ("e_pcred", Pcred),
        ("e_ucred", Ucred),
        ("e_vm", Vmspace),
        ("e_ppid", pid_t),
        ("e_pgid", pid_t),
        ("e_jobc", ctypes.c_short),
        ("e_tdev", dev_t),
        ("e_tpgid", pid_t),
        ("e_tsess", ctypes.c_void_p),
        ("e_wmesg", (ctypes.c_char * (WMESGLEN + 1))),
        ("e_xsize", segsz_t),
        ("e_xrssize", ctypes.c_short),
        ("e_xccount", ctypes.c_short),
        ("e_xswrss", ctypes.c_short),
        ("e_flag", ctypes.c_int32),
        ("e_login", (ctypes.c_char * COMPAT_MAXLOGNAME)),
        ("e_spare", (ctypes.c_int32 * 4)),
    ]


class KinfoProc(ctypes.Structure):
    _fields_ = [
        ("kp_proc", ExternProc),
        ("kp_eproc", Eproc),
    ]

    def get_groups(self) -> List[int]:
        return list(self.kp_eproc.e_ucred.cr_groups[: self.kp_eproc.e_ucred.cr_ngroups])


@_cache.CachedByPid
def _get_kinfo_proc(pid: int) -> KinfoProc:
    if pid <= 0:
        raise ProcessLookupError

    proc_info = KinfoProc()

    length = sysctl([CTL_KERN, KERN_PROC, KERN_PROC_PID, pid], None, proc_info)

    if length == 0:
        raise ProcessLookupError

    return proc_info


def proc_getgroups(pid: int) -> List[int]:
    return _get_kinfo_proc(pid).get_groups()


def proc_get_sigmasks(pid: int) -> ProcessSignalMasks:
    kinfo = _get_kinfo_proc(pid)

    return ProcessSignalMasks(
        ignored=_util.expand_sig_bitmask(kinfo.kp_proc.p_sigignore),
        caught=_util.expand_sig_bitmask(kinfo.kp_proc.p_sigcatch),
    )


def proc_getpgid(pid: int) -> int:
    if _cache.is_enabled(pid):
        # We're in a oneshot_proc(); retrieve extra information
        return cast(int, _get_kinfo_proc(pid).kp_eproc.e_pgid)
    else:
        return _psposix.proc_getpgid(pid)


proc_getsid = _psposix.proc_getsid
