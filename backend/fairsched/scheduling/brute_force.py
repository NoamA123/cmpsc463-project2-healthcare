"""Brute-force optimal solver for small instances. Owner: Noam.

Search over every permutation of patients as a service order. For a given
order, each next patient goes to the earliest-free provider (still alive per
its shift) and starts at ``max(provider_free, arrival_time)``; if that start is
at or past the provider's shift_end the patient is unserved. Minimize
``(number unserved, sum(weight(p, start) * wait))`` lexicographically, ties
broken by the lexicographically smallest order of patient ids. Appointment
``order`` is the rank by ``(start, provider_id)``, as everywhere else.
"""

from __future__ import annotations

from fairsched.schema import Dataset, Schedule, WeightConfig

MAX_BRUTE_FORCE_PATIENTS = 8


def solve_optimal(dataset: Dataset, weights: WeightConfig) -> Schedule:
    """Raises ValueError if the dataset has more than MAX_BRUTE_FORCE_PATIENTS patients."""
    raise NotImplementedError
