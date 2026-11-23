"""Hash table with separate chaining. Owner: Noam.

Used for patient lookup (id -> Patient). Do not wrap ``dict`` here.
"""

from __future__ import annotations

from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class HashTable(Generic[K, V]):
    def __init__(self, capacity: int = 16, max_load: float = 0.75) -> None:
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(capacity)]
        self._size = 0
        self._max_load = max_load

    def __len__(self) -> int:
        return self._size

    def put(self, key: K, value: V) -> None:
        """Insert or overwrite. Resize (double) when load factor exceeds max_load."""
        raise NotImplementedError

    def get(self, key: K) -> V:
        """Raises KeyError if missing."""
        raise NotImplementedError

    def remove(self, key: K) -> V:
        """Remove and return the value. Raises KeyError if missing."""
        raise NotImplementedError

    def __contains__(self, key: object) -> bool:
        raise NotImplementedError

    def keys(self) -> Iterator[K]:
        raise NotImplementedError
