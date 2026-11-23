"""The team's scheduler must match the reference exactly."""

from __future__ import annotations

import pytest

from fairsched import reference
from fairsched.scheduling import brute_force, simulator
from fairsched.schema import Dataset, PolicyName, WeightConfig

ONLINE = [PolicyName.FIFO, PolicyName.SJF, PolicyName.URGENCY, PolicyName.WSPT]
WEIGHTS = [WeightConfig(), WeightConfig(urgency_power=2, group_multipliers={"uninsured": 1.5}, aging_rate=0.1)]


@pytest.mark.parametrize("policy", ONLINE)
@pytest.mark.parametrize("weights", WEIGHTS)
def test_simulator_matches_reference(sample: Dataset, policy: PolicyName, weights: WeightConfig):
    assert simulator.simulate(sample, policy, weights) == reference.simulate(sample, policy, weights)


@pytest.mark.parametrize("weights", WEIGHTS)
def test_brute_force_matches_reference(tiny: Dataset, weights: WeightConfig):
    assert brute_force.solve_optimal(tiny, weights) == reference.solve_optimal(tiny, weights)


def test_brute_force_rejects_large(sample: Dataset):
    if len(sample.patients) <= brute_force.MAX_BRUTE_FORCE_PATIENTS:
        pytest.skip("sample is small")
    with pytest.raises(ValueError):
        brute_force.solve_optimal(sample, WeightConfig())
