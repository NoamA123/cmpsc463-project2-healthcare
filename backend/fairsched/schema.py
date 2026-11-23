"""Standardized input/output format shared by every module and the web app.

This file is the single source of truth for the data contract. The JSON Schema
files in ``/schemas`` are generated from it (``python scripts/export_schemas.py``)
and ``frontend/src/api/types.ts`` mirrors it by hand. If you change a model here,
re-export the schemas and update the TypeScript types in the same commit.

Conventions
-----------
* All times are integer **minutes since the clinic opens** (t = 0).
* ``wait = appointment.start - patient.arrival_time``.
* Urgency is an integer 1 (routine) .. 5 (critical).
* Ties in every policy are broken by ``(arrival_time, id)`` so results are deterministic.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "1.0"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- #
# Inputs: datasets
# --------------------------------------------------------------------------- #


class Patient(_Model):
    id: str = Field(description='Unique id, e.g. "P0001".')
    arrival_time: int = Field(ge=0, description="Minutes since clinic opens.")
    visit_length: int = Field(gt=0, description="Visit duration in minutes.")
    urgency: int = Field(ge=1, le=5, description="1 = routine, 5 = critical.")
    group: str = Field(description="Insurance/income group; must appear in meta.groups.")


class Provider(_Model):
    id: str = Field(description='Unique id, e.g. "D01".')
    name: str
    shift_start: int = Field(default=0, ge=0)
    shift_end: int = Field(gt=0, description="A provider may not START a visit at or after this time.")

    @model_validator(mode="after")
    def _check_shift(self) -> Provider:
        if self.shift_end <= self.shift_start:
            raise ValueError("shift_end must be greater than shift_start")
        return self


class DatasetMeta(_Model):
    name: str
    schema_version: str = SCHEMA_VERSION
    seed: int | None = None
    horizon: int = Field(gt=0, description="Length of the simulated day in minutes.")
    groups: list[str] = Field(min_length=1)
    description: str = ""


class Dataset(_Model):
    meta: DatasetMeta
    providers: list[Provider] = Field(min_length=1)
    patients: list[Patient]

    @model_validator(mode="after")
    def _check_consistency(self) -> Dataset:
        for kind, items in (("patient", self.patients), ("provider", self.providers)):
            ids = [x.id for x in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {kind} ids")
        groups = set(self.meta.groups)
        unknown = {p.group for p in self.patients} - groups
        if unknown:
            raise ValueError(f"patients use groups not listed in meta.groups: {sorted(unknown)}")
        return self


class GeneratorParams(_Model):
    """Knobs for the synthetic dataset generator."""

    name: str = "generated"
    n_patients: int = Field(default=50, ge=1, le=100_000)
    n_providers: int = Field(default=3, ge=1, le=100)
    horizon: int = Field(default=480, gt=0, description="Arrivals fall in [0, horizon).")
    group_mix: dict[str, float] = Field(
        default_factory=lambda: {"private": 0.5, "public": 0.3, "uninsured": 0.2},
        description="Relative frequency of each group (normalized automatically).",
    )
    urgency_weights: list[float] = Field(
        default_factory=lambda: [0.30, 0.30, 0.20, 0.15, 0.05],
        min_length=5,
        max_length=5,
        description="Relative frequency of urgency 1..5.",
    )
    visit_length_min: int = Field(default=10, gt=0)
    visit_length_max: int = Field(default=45, gt=0)
    seed: int | None = 42


# --------------------------------------------------------------------------- #
# Inputs: simulation request
# --------------------------------------------------------------------------- #


class PolicyName(str, Enum):
    FIFO = "fifo"
    SJF = "sjf"
    URGENCY = "urgency"
    WSPT = "wspt"
    OPTIMAL = "optimal"


class WeightConfig(_Model):
    """weight(p, t) = urgency ** urgency_power * group_multipliers.get(group, 1)
    + aging_rate * (t - arrival_time)"""

    urgency_power: float = Field(default=1.0, ge=0)
    group_multipliers: dict[str, float] = Field(default_factory=dict)
    aging_rate: float = Field(default=0.0, ge=0)


class SimulationRequest(_Model):
    dataset: Dataset
    policies: list[PolicyName] = Field(min_length=1)
    weights: WeightConfig = Field(default_factory=WeightConfig)
    top_k: int = Field(default=5, ge=1)


# --------------------------------------------------------------------------- #
# Outputs
# --------------------------------------------------------------------------- #


class Appointment(_Model):
    patient_id: str
    provider_id: str
    start: int
    end: int
    wait: int
    order: int = Field(description="0-based rank of the appointment by (start, provider_id).")


class Schedule(_Model):
    """What a scheduler produces, before analytics."""

    policy: PolicyName
    appointments: list[Appointment]
    unserved: list[str] = Field(description="Patient ids never seen, in arrival order.")


class PatientWait(_Model):
    patient_id: str
    wait: int


class WaitStats(_Model):
    count: int
    mean: float
    median: float
    p90: float
    max: int
    top_k: list[PatientWait] = Field(description="Longest waits, descending.")


class FairnessStats(_Model):
    """Inversions between the service order and a reference ranking.

    ``disagreement_* = inversions / (n * (n - 1) / 2)`` in [0, 1] (0 when n < 2).
    Unserved patients are placed after all served ones, in arrival order.
    """

    n: int
    inversions_vs_arrival: int
    inversions_vs_urgency: int
    disagreement_vs_arrival: float
    disagreement_vs_urgency: float


class GroupMetrics(_Model):
    group: str
    served: int
    unserved: int
    waits: WaitStats
    fairness: FairnessStats


class PolicyMetrics(_Model):
    served: int
    unserved: int
    makespan: int = Field(description="End time of the last appointment.")
    total_weighted_wait: float
    provider_utilization: dict[str, float] = Field(description="Busy minutes / shift minutes, per provider.")
    waits: WaitStats
    fairness: FairnessStats
    per_group: list[GroupMetrics]


class EngineInfo(_Model):
    """Which implementation produced a result: the team's own code, or the
    builtin-based reference in ``fairsched.reference`` used as a fallback."""

    scheduler: str
    analytics: str


class PolicyResult(_Model):
    policy: PolicyName
    schedule: Schedule
    metrics: PolicyMetrics
    engine: EngineInfo
    runtime_ms: float


class SimulationResponse(_Model):
    schema_version: str = SCHEMA_VERSION
    dataset_name: str
    weights: WeightConfig
    results: list[PolicyResult]


class BenchmarkRecord(_Model):
    """One row of benchmark output (written to ``backend/benchmarks/results/*.json``)."""

    task: str = Field(description='e.g. "median", "inversions".')
    algorithm: str = Field(description='e.g. "dselect", "rselect", "sort", "merge_count", "brute_force".')
    n: int
    trials: int
    mean_ms: float
    min_ms: float
