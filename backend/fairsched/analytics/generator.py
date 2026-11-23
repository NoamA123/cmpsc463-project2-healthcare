"""Synthetic dataset generator. Owner: Yony.

Basic working version so the team has data from day one; extend freely
(arrival bursts, group-dependent urgency, per-provider shifts, ...).
"""

from __future__ import annotations

import random

from fairsched.schema import Dataset, DatasetMeta, GeneratorParams, Patient, Provider


def generate(params: GeneratorParams) -> Dataset:
    if not params.group_mix:
        raise ValueError("group_mix must not be empty")
    if params.visit_length_min > params.visit_length_max:
        raise ValueError("visit_length_min must be <= visit_length_max")

    rng = random.Random(params.seed)
    groups = list(params.group_mix)
    group_w = [params.group_mix[g] for g in groups]

    raw = []
    for _ in range(params.n_patients):
        raw.append(
            (
                rng.randrange(params.horizon),
                rng.randint(params.visit_length_min, params.visit_length_max),
                rng.choices(range(1, 6), weights=params.urgency_weights)[0],
                rng.choices(groups, weights=group_w)[0],
            )
        )
    raw.sort(key=lambda r: r[0])
    width = max(4, len(str(params.n_patients)))
    patients = [
        Patient(id=f"P{i + 1:0{width}d}", arrival_time=a, visit_length=v, urgency=u, group=g)
        for i, (a, v, u, g) in enumerate(raw)
    ]
    providers = [
        Provider(id=f"D{i + 1:02d}", name=f"Provider {i + 1}", shift_start=0, shift_end=params.horizon)
        for i in range(params.n_providers)
    ]
    meta = DatasetMeta(
        name=params.name,
        seed=params.seed,
        horizon=params.horizon,
        groups=groups,
        description=f"Synthetic: {params.n_patients} patients, {params.n_providers} providers.",
    )
    return Dataset(meta=meta, providers=providers, patients=patients)
