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
            for item in items:
                self.push(item)

    def __len__(self) -> int:
        return len(self._data)

    def push(self, item: T) -> None:
        """O(log n). Add item to heap by appending to end and sifting up."""
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> T:
        """Remove and return the smallest item. O(log n). Raises IndexError if empty."""
        if not self._data:
            raise IndexError("pop on empty heap")
        if len(self._data) == 1:
            return self._data.pop() # if only one item, return it
        root = self._data[0] # store root to return
        # place last item in root position and sift down
        self._data[0] = self._data.pop()
        self._sift_down(0)
        return root

    def peek(self) -> T:
        """Return the smallest item without removing it. Raises IndexError if empty."""
        if not self._data:
            raise IndexError("peek on empty heap")
        return self._data[0]

    def _sift_up(self, index: int) -> None:
        """Sift up item at index to maintain heap property. Parent index is (index - 1) // 2."""
        parent_idx = (index - 1) // 2
        while index > 0 and self._data[index] < self._data[parent_idx]:
            self._data[index], self._data[parent_idx] = self._data[parent_idx], self._data[index] # swap with parent
            # update indices
            index = parent_idx
            parent_idx = (index - 1) // 2

    def _sift_down(self, index: int) -> None:
        """Sift down item at index to maintain heap property. Children indices are 2*index + 1 and 2*index + 2."""
        left_child_idx = 2 * index + 1
        right_child_idx = 2 * index + 2
        while left_child_idx < len(self._data):
            smallest_child_idx = left_child_idx
            if right_child_idx < len(self._data) and self._data[right_child_idx] < self._data[left_child_idx]:
                smallest_child_idx = right_child_idx
            if not self._data[index] > self._data[smallest_child_idx]:
                break # stop sifting down if item is smaller or equal to smallest child
            # swap with smallest child
            self._data[index], self._data[smallest_child_idx] = self._data[smallest_child_idx], self._data[index]
            # update indices
            index = smallest_child_idx
            left_child_idx = 2 * index + 1
            right_child_idx = 2 * index + 2