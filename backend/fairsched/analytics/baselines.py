"""Naive baselines: sort-based statistics and O(n^2) inversion counting.

These are the "before" side of the runtime benchmarks and the oracles for
correctness tests. Keep them obviously correct rather than fast.
"""

from __future__ import annotations

import math


def sort_select(xs: list[int], k: int) -> int:
    if not 1 <= k <= len(xs):
        raise ValueError(f"k={k} out of range for n={len(xs)}")
    return sorted(xs)[k - 1]


def sort_median(xs: list[int]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("median of empty list")
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def sort_percentile(xs: list[int], p: float) -> int:
    return sort_select(xs, max(1, math.ceil(p / 100 * len(xs))))


def sort_top_k(xs: list[int], k: int) -> list[int]:
    return sorted(xs, reverse=True)[:k]


def brute_force_inversions(xs: list[int]) -> int:
    n = len(xs)
    return sum(1 for i in range(n) for j in range(i + 1, n) if xs[i] > xs[j])
