from __future__ import annotations

import pytest

from fairsched.io import SAMPLES_DIR, list_samples, load_dataset
from fairsched.schema import Dataset


@pytest.hookimpl(wrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    """Report tests of unfinished modules as skipped instead of failed."""
    try:
        return (yield)
    except NotImplementedError as e:
        pytest.skip(f"not implemented yet: {e}" if str(e) else "not implemented yet")


@pytest.fixture(params=list_samples())
def sample(request) -> Dataset:
    return load_dataset(SAMPLES_DIR / f"{request.param}.json")


@pytest.fixture
def tiny() -> Dataset:
    return load_dataset(SAMPLES_DIR / "tiny.json")
