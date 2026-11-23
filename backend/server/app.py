"""HTTP API for the web app. Run from ``backend/``:

    uvicorn server.app:app --reload

Interactive docs at http://localhost:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fairsched import engine
from fairsched.analytics.generator import generate
from fairsched.io import SAMPLES_DIR, list_samples, load_dataset
from fairsched.scheduling.brute_force import MAX_BRUTE_FORCE_PATIENTS
from fairsched.scheduling.policies import POLICY_DESCRIPTIONS
from fairsched.schema import SCHEMA_VERSION, Dataset, GeneratorParams, PolicyName, SimulationRequest, SimulationResponse

app = FastAPI(title="Fair Appointment Scheduler", version=SCHEMA_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PolicyInfo(BaseModel):
    name: PolicyName
    description: str
    max_patients: int | None = None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "schema_version": SCHEMA_VERSION}


@app.get("/api/policies")
def policies() -> list[PolicyInfo]:
    return [
        PolicyInfo(
            name=p,
            description=POLICY_DESCRIPTIONS[p],
            max_patients=MAX_BRUTE_FORCE_PATIENTS if p == PolicyName.OPTIMAL else None,
        )
        for p in PolicyName
    ]


@app.get("/api/datasets")
def datasets() -> list[str]:
    return list_samples()


@app.get("/api/datasets/{name}")
def dataset(name: str) -> Dataset:
    if name not in list_samples():
        raise HTTPException(404, f"unknown sample dataset {name!r}")
    return load_dataset(SAMPLES_DIR / f"{name}.json")


@app.post("/api/datasets/generate")
def generate_dataset(params: GeneratorParams) -> Dataset:
    try:
        return generate(params)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@app.post("/api/simulate")
def simulate(req: SimulationRequest) -> SimulationResponse:
    if PolicyName.OPTIMAL in req.policies and len(req.dataset.patients) > MAX_BRUTE_FORCE_PATIENTS:
        raise HTTPException(422, f"optimal policy supports at most {MAX_BRUTE_FORCE_PATIENTS} patients")
    try:
        return engine.run_simulation(req)
    except NotImplementedError as e:
        raise HTTPException(501, f"not implemented yet: {e}") from e
