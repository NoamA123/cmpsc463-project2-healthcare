"""Sanity checks on the reference engine, which every other test trusts."""

from __future__ import annotations

import pytest

from fairsched import reference
from fairsched.schema import Dataset, PolicyName, Schedule, WeightConfig

ONLINE = [PolicyName.FIFO, PolicyName.SJF, PolicyName.URGENCY, PolicyName.WSPT]


def check_valid_schedule(ds: Dataset, s: Schedule) -> None:
    patients = {p.id: p for p in ds.patients}
    providers = {p.id: p for p in ds.providers}
    seen = [a.patient_id for a in s.appointments] + s.unserved
    assert sorted(seen) == sorted(patients)
    assert [a.order for a in s.appointments] == list(range(len(s.appointments)))
    by_provider: dict[str, list] = {}
    for a in s.appointments:
        p, pr = patients[a.patient_id], providers[a.provider_id]
        assert a.start >= p.arrival_time and a.wait == a.start - p.arrival_time
        assert a.end - a.start == p.visit_length
        assert pr.shift_start <= a.start < pr.shift_end
        by_provider.setdefault(a.provider_id, []).append(a)
    for appts in by_provider.values():
        appts.sort(key=lambda a: a.start)
        assert all(x.end <= y.start for x, y in zip(appts, appts[1:]))


@pytest.mark.parametrize("policy", ONLINE)
def test_reference_schedules_are_valid(sample: Dataset, policy: PolicyName):
    check_valid_schedule(sample, reference.simulate(sample, policy, WeightConfig()))


def test_tiny_fifo_by_hand(tiny: Dataset):
    s = reference.simulate(tiny, PolicyName.FIFO, WeightConfig())
    assert {a.patient_id: a.start for a in s.appointments} == {
        "P01": 0, "P02": 5, "P03": 15, "P04": 30, "P05": 35, "P06": 35,
    }


def test_tiny_urgency_by_hand(tiny: Dataset):
    s = reference.simulate(tiny, PolicyName.URGENCY, WeightConfig())
    assert {a.patient_id: a.start for a in s.appointments} == {
        "P01": 0, "P02": 5, "P04": 15, "P05": 20, "P03": 30, "P06": 50,
    }


def test_optimal_beats_every_policy(tiny: Dataset):
    w = WeightConfig(urgency_power=2)
    best = reference.compute_metrics(tiny, reference.solve_optimal(tiny, w), w).total_weighted_wait
    for policy in ONLINE:
        m = reference.compute_metrics(tiny, reference.simulate(tiny, policy, w), w)
        assert best <= m.total_weighted_wait + 1e-9


def test_fifo_has_no_arrival_inversions(sample: Dataset):
    s = reference.simulate(sample, PolicyName.FIFO, WeightConfig())
    assert reference.compute_metrics(sample, s, WeightConfig()).fairness.inversions_vs_arrival == 0
