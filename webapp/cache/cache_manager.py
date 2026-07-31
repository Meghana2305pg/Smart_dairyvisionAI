"""Simple in-process cache utilities for the Streamlit frontend."""

from __future__ import annotations

from threading import RLock
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class CacheManager:
    """A lightweight cache for values reused across Streamlit pages."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._lock = RLock()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = value

    def get_or_set(self, key: str, factory: Callable[[], T]) -> T:
        with self._lock:
            if key not in self._store:
                self._store[key] = factory()
            return self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
