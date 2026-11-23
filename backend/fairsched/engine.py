"""Glue between the team's modules and the outside world (API, scripts, tests).

Engine selection via the ``FAIRSCHED_ENGINE`` environment variable:
* ``auto`` (default): use the team's module, fall back to ``reference`` if it
  raises NotImplementedError.
* ``team``: team modules only; NotImplementedError propagates.
* ``reference``: reference implementation only.
"""

from __future__ import annotations

import os
import time
from typing import Callable, TypeVar

from fairsched import reference
from fairsched.analytics import metrics as team_metrics
from fairsched.scheduling import brute_force, simulator
from fairsched.schema import (
    Dataset,
    EngineInfo,
    PolicyName,
    PolicyResult,
    SimulationRequest,
    SimulationResponse,
    WeightConfig,
)

R = TypeVar("R")


def _pick(team: Callable[[], R], ref: Callable[[], R]) -> tuple[R, str]:
    mode = os.environ.get("FAIRSCHED_ENGINE", "auto")
    if mode == "reference":
        return ref(), "reference"
    try:
        return team(), "team"
    except NotImplementedError:
        if mode == "team":
            raise
        return ref(), "reference"


def run_policy(dataset: Dataset, policy: PolicyName, weights: WeightConfig, top_k: int = 5) -> PolicyResult:
    t0 = time.perf_counter()
    if policy == PolicyName.OPTIMAL:
        schedule, sched_engine = _pick(
            lambda: brute_force.solve_optimal(dataset, weights),
            lambda: reference.solve_optimal(dataset, weights),
        )
    else:
        schedule, sched_engine = _pick(
            lambda: simulator.simulate(dataset, policy, weights),
            lambda: reference.simulate(dataset, policy, weights),
        )
    metrics, analytics_engine = _pick(
        lambda: team_metrics.compute_metrics(dataset, schedule, weights, top_k),
        lambda: reference.compute_metrics(dataset, schedule, weights, top_k),
    )
    return PolicyResult(
        policy=policy,
        schedule=schedule,
        metrics=metrics,
        engine=EngineInfo(scheduler=sched_engine, analytics=analytics_engine),
        runtime_ms=(time.perf_counter() - t0) * 1000,
    )


def run_simulation(req: SimulationRequest) -> SimulationResponse:
    return SimulationResponse(
        dataset_name=req.dataset.meta.name,
        weights=req.weights,
        results=[run_policy(req.dataset, p, req.weights, req.top_k) for p in req.policies],
    )
