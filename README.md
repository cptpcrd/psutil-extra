# psutil-extra

[![PyPI](https://img.shields.io/pypi/v/psutil-extra)](https://pypi.org/project/psutil-extra)
[![Python Versions](https://img.shields.io/pypi/pyversions/psutil-extra)](https://pypi.org/project/psutil-extra)
[![Documentation Status](https://readthedocs.org/projects/psutil-extra/badge/?version=latest)](https://psutil-extra.readthedocs.io/en/latest/)
[![GitHub Actions](https://github.com/cptpcrd/psutil-extra/workflows/CI/badge.svg?branch=master&event=push)](https://github.com/cptpcrd/psutil-extra/actions?query=workflow%3ACI+branch%3Amaster+event%3Apush)
[![Cirrus CI](https://api.cirrus-ci.com/github/cptpcrd/psutil-extra.svg?branch=master)](https://cirrus-ci.com/github/cptpcrd/psutil-extra)
[![codecov](https://codecov.io/gh/cptpcrd/psutil-extra/branch/master/graph/badge.svg)](https://codecov.io/gh/cptpcrd/psutil-extra)

Some helper functions to go along with the ones in psutil.

[Documentation](https://psutil-extra.readthedocs.io/en/latest/)

## Examples

```
>>> import os
>>> import resource
>>> import psutil
>>> import psutil_extra
>>> proc = psutil.Process()
>>> os.getgroups()
[1000]
>>> psutil_extra.proc_getgroups(proc)  # Availability: Linux, macOS, FreeBSD, OpenBSD, NetBSD, DragonFlyBSD, Solaris
[1000]
>>> psutil_extra.proc_get_umask(proc)  # Availability: Linux (kernel 4.7 or newer), FreeBSD
18
>>> resource.getrlimit(resource.RLIMIT_NOFILE)
(1024, 524288)
>>> psutil_extra.proc_rlimit(proc, resource.RLIMIT_NOFILE)  # Availability: Linux, FreeBSD, NetBSD
(1024, 524288)
>>> psutil_extra.proc_get_sigmasks()  # Availability: Linux, macOS, FreeBSD, OpenBSD, NetBSD, DragonFlyBSD
ProcessSignalMasks(pending=set(), blocked=set(), ignored={25, 13}, caught={32, 33, 2, 28}, process_pending=set())
```

## Platform support

The following platforms have first-class support (the CI builds run tests on these platforms, and all available interfaces should work properly):

- Linux
- macOS
- FreeBSD

In addition, `psutil_extra` *should* work on the following platforms, but no testing has been performed:

- OpenBSD
- NetBSD
- DragonFlyBSD
- Solaris

Some notes:

- Windows support is not planned. Most of the interfaces that `psutil_extra` currently supports are fairly Unix-specific.
- Most of `psutil_extra`'s interfaces work on Windows Subsystem for Linux, but some of them don't work properly on WSL 1. See the documentation for more details.
