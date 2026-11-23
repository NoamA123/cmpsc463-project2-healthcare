"""The team's analytics must match the sort-based / brute-force baselines exactly."""

from __future__ import annotations

import random

import pytest

from fairsched import reference
from fairsched.analytics import baselines, inversions, metrics, selection
from fairsched.analytics.generator import generate
from fairsched.schema import Dataset, GeneratorParams, PolicyName, WeightConfig


def random_lists():
    rng = random.Random(42)
    yield [7]
    yield [3, 3, 3, 3]
    yield list(range(50, 0, -1))
    for n in (2, 9, 100, 1001):
        yield [rng.randrange(n) for _ in range(n)]


@pytest.mark.parametrize("method", ["rselect", "dselect"])
def test_selection_matches_sort(method: str):
    for xs in random_lists():
        fn = selection.rselect if method == "rselect" else selection.dselect
        for k in {1, len(xs), (len(xs) + 1) // 2}:
            assert fn(list(xs), k) == baselines.sort_select(xs, k)
        assert selection.median(xs, method) == baselines.sort_median(xs)
        assert selection.percentile(xs, 90, method) == baselines.sort_percentile(xs, 90)
        assert selection.top_k(xs, 3, method) == baselines.sort_top_k(xs, 3)


def test_selection_does_not_mutate_input():
    xs = [5, 1, 4, 2, 3]
    selection.dselect(xs, 2)
    assert xs == [5, 1, 4, 2, 3]


def test_inversions_match_brute_force():
    rng = random.Random(7)
    assert inversions.count_inversions([]) == 0
    assert inversions.count_inversions(list(range(10))) == 0
    assert inversions.count_inversions(list(range(10, 0, -1))) == 45
    for n in (2, 17, 500):
        xs = rng.sample(range(n), n)
        assert inversions.count_inversions(xs) == baselines.brute_force_inversions(xs)


@pytest.mark.parametrize("policy", [PolicyName.FIFO, PolicyName.WSPT])
def test_metrics_match_reference(sample: Dataset, policy: PolicyName):
    w = WeightConfig(urgency_power=2)
    s = reference.simulate(sample, policy, w)
    assert metrics.compute_metrics(sample, s, w, 5) == reference.compute_metrics(sample, s, w, 5)


def test_generator_is_deterministic_and_valid():
    p = GeneratorParams(n_patients=100, n_providers=4, seed=9)
    a, b = generate(p), generate(p)
    assert a == b
    assert len(a.patients) == 100 and len(a.providers) == 4
    assert all(0 <= x.arrival_time < p.horizon for x in a.patients)
    assert [x.arrival_time for x in a.patients] == sorted(x.arrival_time for x in a.patients)
