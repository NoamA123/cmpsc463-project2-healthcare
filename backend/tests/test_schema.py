from __future__ import annotations

import pytest
from pydantic import ValidationError

from fairsched.io import REPO_ROOT
from fairsched.schema import Dataset, SimulationRequest, SimulationResponse


def test_samples_are_valid(sample: Dataset):
    assert sample.patients


def test_examples_are_valid():
    ex = REPO_ROOT / "data" / "examples"
    SimulationRequest.model_validate_json((ex / "simulation_request.json").read_text())
    SimulationResponse.model_validate_json((ex / "simulation_response.json").read_text())


def test_rejects_unknown_group(tiny: Dataset):
    data = tiny.model_dump()
    data["patients"][0]["group"] = "martian"
    with pytest.raises(ValidationError):
        Dataset.model_validate(data)


def test_rejects_duplicate_ids(tiny: Dataset):
    data = tiny.model_dump()
    data["patients"][1]["id"] = data["patients"][0]["id"]
    with pytest.raises(ValidationError):
        Dataset.model_validate(data)


def test_rejects_extra_fields(tiny: Dataset):
    data = tiny.model_dump()
    data["patients"][0]["insurance"] = "x"
    with pytest.raises(ValidationError):
        Dataset.model_validate(data)
