import contextlib
import threading
from typing import Any, Callable, Generic, Iterable, TypeVar, cast

_cache_store = threading.local()


def get_cache(pid: int, name: str) -> Any:
    """Raises KeyError if value not found"""
    return _cache_store.__dict__[pid][name]  # type: ignore


def store_cache(pid: int, name: str, value: Any) -> None:
    try:
        data = _cache_store.__dict__[pid]  # type: ignore
    except KeyError:
        pass
    else:
        data[name] = value


def is_enabled(pid: int) -> bool:
    return pid in _cache_store.__dict__  # type: ignore


T = TypeVar("T")


class CachedByPid(Generic[T]):
    def __init__(self, func: Callable[[int], T]):
        self._func = func
        self._name = self.__class__.__name__ + "-" + func.__module__ + "." + func.__name__

    def get_cached_value(self, pid: int) -> T:
        return cast(T, get_cache(pid, self._name))  # pytype: disable=invalid-typevar

    def __call__(self, pid: int) -> T:
        try:
            return self.get_cached_value(pid)
        except KeyError:
            pass

        value = self._func(pid)
        store_cache(pid, self._name, value)
        return value


@contextlib.contextmanager  # type: ignore
def oneshot_proc(pid: int) -> Iterable[None]:  # pytype: disable=wrong-arg-types
    if is_enabled(pid):
        yield
    else:
        _cache_store.__dict__[pid] = {}  # type: ignore

        try:
            yield
        finally:
            _cache_store.__dict__.pop(pid, None)  # type: ignore
