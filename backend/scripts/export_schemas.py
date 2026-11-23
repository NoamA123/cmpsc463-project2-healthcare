"""Export JSON Schema files for the data contract into /schemas.

    cd backend
    python -m scripts.export_schemas
"""

from __future__ import annotations

import json

from fairsched import schema
from fairsched.io import REPO_ROOT

MODELS = {
    "dataset": schema.Dataset,
    "generator_params": schema.GeneratorParams,
    "simulation_request": schema.SimulationRequest,
    "simulation_response": schema.SimulationResponse,
    "benchmark_record": schema.BenchmarkRecord,
}


def main() -> None:
    out = REPO_ROOT / "schemas"
    out.mkdir(exist_ok=True)
    for name, model in MODELS.items():
        path = out / f"{name}.schema.json"
        path.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n", encoding="utf-8")
        print(f"wrote schemas/{path.name}")


if __name__ == "__main__":
    main()
