"""Regenerate the committed sample datasets and example request/response.

    cd backend
    python -m scripts.make_sample_data
"""

from __future__ import annotations

from fairsched import engine
from fairsched.analytics.generator import generate
from fairsched.io import REPO_ROOT, SAMPLES_DIR, save_json
from fairsched.schema import (
    Dataset,
    DatasetMeta,
    GeneratorParams,
    Patient,
    PolicyName,
    Provider,
    SimulationRequest,
    WeightConfig,
)

EXAMPLES_DIR = REPO_ROOT / "data" / "examples"


def tiny() -> Dataset:
    """Hand-built, small enough to check by hand and to brute-force."""
    rows = [
        ("P01", 0, 30, 1, "private"),
        ("P02", 5, 10, 4, "uninsured"),
        ("P03", 10, 20, 2, "public"),
        ("P04", 12, 5, 5, "uninsured"),
        ("P05", 15, 40, 3, "private"),
        ("P06", 20, 15, 2, "public"),
    ]
    return Dataset(
        meta=DatasetMeta(
            name="tiny",
            horizon=120,
            groups=["private", "public", "uninsured"],
            description="6 hand-written patients, 2 providers. Small enough for the optimal policy.",
        ),
        providers=[
            Provider(id="D01", name="Dr. Adams", shift_start=0, shift_end=120),
            Provider(id="D02", name="Dr. Baker", shift_start=0, shift_end=120),
        ],
        patients=[Patient(id=i, arrival_time=a, visit_length=v, urgency=u, group=g) for i, a, v, u, g in rows],
    )


def main() -> None:
    datasets = [
        tiny(),
        # Mean visit is ~27.5 min, so load ~= n_patients * 27.5 / (n_providers * horizon).
        generate(GeneratorParams(name="small", n_patients=30, n_providers=4, horizon=240, seed=1)),
        generate(GeneratorParams(name="medium", n_patients=200, n_providers=12, horizon=480, seed=2)),
        generate(
            GeneratorParams(
                name="overloaded",
                n_patients=45,
                n_providers=2,
                horizon=480,
                seed=3,
                group_mix={"private": 0.4, "public": 0.35, "uninsured": 0.25},
            )
        ),
    ]
    for ds in datasets:
        save_json(ds, SAMPLES_DIR / f"{ds.meta.name}.json")
        print(f"wrote data/samples/{ds.meta.name}.json ({len(ds.patients)} patients)")

    request = SimulationRequest(
        dataset=datasets[0],
        policies=list(PolicyName),
        weights=WeightConfig(urgency_power=2.0, group_multipliers={"uninsured": 1.5}, aging_rate=0.05),
        top_k=3,
    )
    save_json(request, EXAMPLES_DIR / "simulation_request.json")
    save_json(engine.run_simulation(request), EXAMPLES_DIR / "simulation_response.json")
    print("wrote data/examples/simulation_request.json and simulation_response.json")


if __name__ == "__main__":
    main()
