"""Efficiency and fairness metrics for one schedule. Owner: Yony.

Must produce exactly what ``fairsched.reference.compute_metrics`` produces,
but using ``selection`` (dselect) and ``inversions`` (merge count) instead of
sorting and O(n^2) loops. Rules:

* Wait stats cover served patients only; if none are served, every number is 0.
* top_k ties are broken by patient_id ascending.
* Fairness service order = served patients by ``appointment.order``, then
  unserved patients in arrival order.
* Reference rankings: arrival = by (arrival_time, id);
  urgency = by (-urgency, arrival_time, id).
* Per-group metrics restrict both the service order and the reference ranking
  to that group's patients. Groups come from ``dataset.meta.groups`` in order.
* total_weighted_wait = sum(weight(p, start) * wait) over served patients.
* provider_utilization = busy minutes / (shift_end - shift_start).
"""

from __future__ import annotations

from fairsched.schema import Dataset, PolicyMetrics, Schedule, WeightConfig


def compute_metrics(dataset: Dataset, schedule: Schedule, weights: WeightConfig, top_k: int = 5) -> PolicyMetrics:
    raise NotImplementedError
