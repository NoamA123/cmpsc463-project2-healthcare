"""Reference implementation built on Python builtins (heapq, sorted, itertools).

NOT part of the graded algorithms. It exists so that:
* tests have an oracle to compare the team's implementations against, and
* the web app works end to end before the real modules are finished.
``fairsched.engine`` only falls back to this when a team module raises
NotImplementedError, and records that in ``PolicyResult.engine``.
"""

from __future__ import annotations

import heapq
from itertools import permutations

from fairsched.analytics.baselines import brute_force_inversions, sort_median, sort_percentile
from fairsched.analytics.inversions import normalized
from fairsched.scheduling.brute_force import MAX_BRUTE_FORCE_PATIENTS
from fairsched.scheduling.policies import make_key, weight
from fairsched.schema import (
    Appointment,
    Dataset,
    FairnessStats,
    GroupMetrics,
    Patient,
    PatientWait,
    PolicyMetrics,
    PolicyName,
    Provider,
    Schedule,
    WaitStats,
    WeightConfig,
)


def _arrival_key(p: Patient) -> tuple:
    return (p.arrival_time, p.id)


def _finalize(policy: PolicyName, appts: list[Appointment], patients: list[Patient]) -> Schedule:
    appts.sort(key=lambda a: (a.start, a.provider_id))
    for i, a in enumerate(appts):
        a.order = i
    served = {a.patient_id for a in appts}
    unserved = [p.id for p in sorted(patients, key=_arrival_key) if p.id not in served]
    return Schedule(policy=policy, appointments=appts, unserved=unserved)


def simulate(dataset: Dataset, policy: PolicyName, weights: WeightConfig) -> Schedule:
    key = make_key(policy, weights)
    patients = sorted(dataset.patients, key=_arrival_key)
    providers = {pr.id: pr for pr in dataset.providers}
    heap = [(pr.shift_start, pr.id) for pr in dataset.providers]
    heapq.heapify(heap)
    waiting: list[Patient] = []
    nxt = 0
    appts: list[Appointment] = []

    while heap:
        t, pid = heapq.heappop(heap)
        if t >= providers[pid].shift_end:
            continue
        while nxt < len(patients) and patients[nxt].arrival_time <= t:
            waiting.append(patients[nxt])
            nxt += 1
        if not waiting:
            if nxt < len(patients):
                heapq.heappush(heap, (patients[nxt].arrival_time, pid))
                continue
            break
        best = min(waiting, key=lambda p: key(p, t))
        waiting.remove(best)
        end = t + best.visit_length
        appts.append(
            Appointment(patient_id=best.id, provider_id=pid, start=t, end=end, wait=t - best.arrival_time, order=0)
        )
        heapq.heappush(heap, (end, pid))

    return _finalize(policy, appts, dataset.patients)


def _dispatch_in_order(
    order: tuple[Patient, ...], providers: list[Provider], weights: WeightConfig
) -> tuple[tuple[int, float], list[Appointment]]:
    shift_end = {pr.id: pr.shift_end for pr in providers}
    heap = [(pr.shift_start, pr.id) for pr in providers]
    heapq.heapify(heap)
    appts: list[Appointment] = []
    unserved = 0
    cost = 0.0
    for p in order:
        while heap and heap[0][0] >= shift_end[heap[0][1]]:
            heapq.heappop(heap)
        if not heap:
            unserved += 1
            continue
        free, pid = heapq.heappop(heap)
        start = max(free, p.arrival_time)
        if start >= shift_end[pid]:
            unserved += 1
            heapq.heappush(heap, (free, pid))
            continue
        wait = start - p.arrival_time
        cost += weight(p, start, weights) * wait
        appts.append(
            Appointment(patient_id=p.id, provider_id=pid, start=start, end=start + p.visit_length, wait=wait, order=0)
        )
        heapq.heappush(heap, (start + p.visit_length, pid))
    return (unserved, cost), appts


def solve_optimal(dataset: Dataset, weights: WeightConfig) -> Schedule:
    if len(dataset.patients) > MAX_BRUTE_FORCE_PATIENTS:
        raise ValueError(f"optimal policy supports at most {MAX_BRUTE_FORCE_PATIENTS} patients")
    best: tuple[tuple[int, float], list[Appointment]] | None = None
    for order in permutations(sorted(dataset.patients, key=lambda p: p.id)):
        cost, appts = _dispatch_in_order(order, dataset.providers, weights)
        if best is None or cost < best[0]:
            best = (cost, appts)
    return _finalize(PolicyName.OPTIMAL, best[1] if best else [], dataset.patients)


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #


def _wait_stats(waits: list[tuple[str, int]], k: int) -> WaitStats:
    if not waits:
        return WaitStats(count=0, mean=0.0, median=0.0, p90=0.0, max=0, top_k=[])
    vals = [w for _, w in waits]
    top = sorted(waits, key=lambda x: (-x[1], x[0]))[:k]
    return WaitStats(
        count=len(vals),
        mean=sum(vals) / len(vals),
        median=sort_median(vals),
        p90=float(sort_percentile(vals, 90)),
        max=max(vals),
        top_k=[PatientWait(patient_id=pid, wait=w) for pid, w in top],
    )


def _fairness(service_order: list[Patient]) -> FairnessStats:
    n = len(service_order)

    def inversions_vs(ref_key) -> int:
        rank = {p.id: i for i, p in enumerate(sorted(service_order, key=ref_key))}
        return brute_force_inversions([rank[p.id] for p in service_order])

    inv_a = inversions_vs(_arrival_key)
    inv_u = inversions_vs(lambda p: (-p.urgency, p.arrival_time, p.id))
    return FairnessStats(
        n=n,
        inversions_vs_arrival=inv_a,
        inversions_vs_urgency=inv_u,
        disagreement_vs_arrival=normalized(inv_a, n),
        disagreement_vs_urgency=normalized(inv_u, n),
    )


def compute_metrics(dataset: Dataset, schedule: Schedule, weights: WeightConfig, top_k: int = 5) -> PolicyMetrics:
    by_id = {p.id: p for p in dataset.patients}
    appts = sorted(schedule.appointments, key=lambda a: a.order)
    service_order = [by_id[a.patient_id] for a in appts] + [by_id[pid] for pid in schedule.unserved]
    waits = [(a.patient_id, a.wait) for a in appts]

    busy: dict[str, int] = {pr.id: 0 for pr in dataset.providers}
    for a in appts:
        busy[a.provider_id] += a.end - a.start
    utilization = {pr.id: busy[pr.id] / (pr.shift_end - pr.shift_start) for pr in dataset.providers}

    per_group = []
    for g in dataset.meta.groups:
        g_order = [p for p in service_order if p.group == g]
        g_waits = [(pid, w) for pid, w in waits if by_id[pid].group == g]
        per_group.append(
            GroupMetrics(
                group=g,
                served=len(g_waits),
                unserved=len(g_order) - len(g_waits),
                waits=_wait_stats(g_waits, top_k),
                fairness=_fairness(g_order),
            )
        )

    return PolicyMetrics(
        served=len(appts),
        unserved=len(schedule.unserved),
        makespan=max((a.end for a in appts), default=0),
        total_weighted_wait=sum(weight(by_id[a.patient_id], a.start, weights) * a.wait for a in appts),
        provider_utilization=utilization,
        waits=_wait_stats(waits, top_k),
        fairness=_fairness(service_order),
        per_group=per_group,
    )
