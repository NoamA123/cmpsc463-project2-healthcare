"""Binary search tree of open appointment slots. Owner: Noam.

Each provider keeps a ``SlotTree`` of free slots keyed on start time. Used for
cancellations and rebooking: when a visit is cancelled its slot is inserted,
and a rebooked patient takes the earliest open slot >= some time t.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Slot:
    start: int
    end: int
    provider_id: str

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class _Node:
    slot: Slot
    left: _Node | None = None
    right: _Node | None = None


class SlotTree:
    """Ordered by ``slot.start`` (ties broken by the full Slot ordering)."""

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, slot: Slot) -> None:
        raise NotImplementedError

    def delete(self, slot: Slot) -> None:
        """Remove an exact slot. Raises KeyError if absent."""
        raise NotImplementedError

    def earliest_at_or_after(self, t: int, min_length: int = 0) -> Slot | None:
        """Earliest slot with start >= t and length >= min_length, or None."""
        raise NotImplementedError

    def in_order(self) -> list[Slot]:
        raise NotImplementedError
