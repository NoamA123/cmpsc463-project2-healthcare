"""Order statistics via randomized and deterministic selection. Owner: Yony.

Definitions (shared with ``baselines.py`` so results can be compared exactly):
* ``select(xs, k)`` returns the k-th smallest, **1-indexed** (1 <= k <= n).
* median of n values: the middle value if n is odd, otherwise the mean of the
  (n/2)-th and (n/2 + 1)-th smallest.
* percentile(p) uses nearest rank: the ceil(p/100 * n)-th smallest (min rank 1).
* top_k: the k largest values, descending.
Do not sort the whole list in this module; that is the baseline being beaten.
"""

from __future__ import annotations

import random


def rselect(xs: list[int], k: int, rng: random.Random | None = None) -> int:
    """Randomized selection, expected O(n)."""
    raise NotImplementedError


def dselect(xs: list[int], k: int) -> int:
    """Deterministic median-of-medians selection, worst-case O(n)."""
    raise NotImplementedError


def median(xs: list[int], method: str = "dselect") -> float:
    raise NotImplementedError


def percentile(xs: list[int], p: float, method: str = "dselect") -> int:
    raise NotImplementedError


def top_k(xs: list[int], k: int, method: str = "dselect") -> list[int]:
    """Find the threshold with selection, then collect and sort only the k results."""
    raise NotImplementedError
