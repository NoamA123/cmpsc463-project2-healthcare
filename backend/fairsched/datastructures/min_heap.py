"""Array-backed binary min-heap. Owner: Noam.

Used to dispatch patients to providers: keyed on ``(next_free_time, provider_id)``
so the earliest-available provider is always at the top.
Do not use ``heapq`` here; that is what this module replaces.
"""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    """Items must be mutually comparable (tuples work well)."""

    def __init__(self, items: list[T] | None = None) -> None:
        self._data: list[T] = []
        if items:
            raise NotImplementedError("heapify in O(n)")

    def __len__(self) -> int:
        return len(self._data)

    def push(self, item: T) -> None:
        """O(log n)."""
        raise NotImplementedError

    def pop(self) -> T:
        """Remove and return the smallest item. O(log n). Raises IndexError if empty."""
        raise NotImplementedError

    def peek(self) -> T:
        """Return the smallest item without removing it. Raises IndexError if empty."""
        raise NotImplementedError
