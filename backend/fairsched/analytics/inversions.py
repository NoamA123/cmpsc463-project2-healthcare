"""Ranking disagreement via inversion counting. Owner: Yony.

An inversion is a pair i < j with xs[i] > xs[j]. To compare a policy against a
reference ranking, map each patient to its reference rank and list those ranks
in service order; the inversion count of that list is the disagreement.
"""

from __future__ import annotations


def count_inversions(xs: list[int]) -> int:
    """Merge-sort based, O(n log n)."""
    raise NotImplementedError


def normalized(inversions: int, n: int) -> float:
    """inversions / (n choose 2), or 0.0 when n < 2."""
    return 0.0 if n < 2 else inversions / (n * (n - 1) / 2)
