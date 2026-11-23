"""Online simulation loop. Owner: Noam.

Semantics (the reference implementation in ``fairsched.reference`` follows
these exactly, so results must match it):

1. Put every provider in a MinHeap keyed ``(max(shift_start, 0), provider_id)``.
2. Pop the earliest-free provider at time ``t``. If ``t >= shift_end`` the
   provider is done for the day (do not push it back).
3. Waiting = patients with ``arrival_time <= t`` not yet served.
   * If empty and patients remain: push the provider back at the next arrival time.
   * If empty and none remain: stop.
4. Otherwise serve the waiting patient with the smallest ``policy key(p, t)``:
   ``start = t``, ``end = t + visit_length``; push the provider back at ``end``.
5. Patients never served are ``unserved`` (listed in arrival order).
"""

from __future__ import annotations

from fairsched.schema import Dataset, PolicyName, Schedule, WeightConfig


def simulate(dataset: Dataset, policy: PolicyName, weights: WeightConfig) -> Schedule:
    """Run one online policy (fifo, sjf, urgency, wspt) over the dataset.

    Use MinHeap for provider dispatch and HashTable for patient lookup.
    """
    raise NotImplementedError
