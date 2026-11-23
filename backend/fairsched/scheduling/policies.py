"""Scheduling policies. Owner: Noam.

A policy is a priority key: whenever a provider frees up at time ``t``, the
waiting patient with the SMALLEST key is served next. Every key ends in
``(arrival_time, id)`` so ties are deterministic across implementations.
"""

from __future__ import annotations

from typing import Callable

from fairsched.schema import Patient, PolicyName, WeightConfig

PriorityKey = Callable[[Patient, int], tuple]


def weight(p: Patient, t: int, cfg: WeightConfig) -> float:
    """Importance of serving ``p`` at time ``t`` (see WeightConfig)."""
    base = p.urgency**cfg.urgency_power * cfg.group_multipliers.get(p.group, 1.0)
    return base + cfg.aging_rate * max(0, t - p.arrival_time)


def make_key(policy: PolicyName, cfg: WeightConfig) -> PriorityKey:
    if policy == PolicyName.FIFO:
        return lambda p, t: (p.arrival_time, p.id)
    if policy == PolicyName.SJF:
        return lambda p, t: (p.visit_length, p.arrival_time, p.id)
    if policy == PolicyName.URGENCY:
        return lambda p, t: (-p.urgency, p.arrival_time, p.id)
    if policy == PolicyName.WSPT:
        return lambda p, t: (-weight(p, t, cfg) / p.visit_length, p.arrival_time, p.id)
    raise ValueError(f"{policy.value!r} is not an online priority policy")


POLICY_DESCRIPTIONS: dict[PolicyName, str] = {
    PolicyName.FIFO: "First come, first served (baseline).",
    PolicyName.SJF: "Shortest visit first (baseline).",
    PolicyName.URGENCY: "Highest urgency first (baseline).",
    PolicyName.WSPT: "Greedy by weight / visit length (Smith's rule).",
    PolicyName.OPTIMAL: "Brute-force minimum total weighted wait (small instances only).",
}
