# Data format (schema v1.0)

Source of truth: `backend/fairsched/schema.py`. Generated JSON Schemas:
`schemas/*.schema.json`. TypeScript mirror: `frontend/src/api/types.ts`.
Full worked example: `data/examples/simulation_request.json` →
`data/examples/simulation_response.json`.

## Conventions

* Times are **integer minutes since the clinic opens** (t = 0).
* `wait = start - arrival_time`.
* `urgency` is 1 (routine) to 5 (critical).
* Every policy breaks ties by `(arrival_time, id)`, so output is deterministic.
* Unknown fields are rejected (`extra = "forbid"`), which catches typos early.

## Input: `Dataset`

```json
{
  "meta": {
    "name": "tiny",
    "schema_version": "1.0",
    "seed": null,
    "horizon": 120,
    "groups": ["private", "public", "uninsured"],
    "description": "..."
  },
  "providers": [
    { "id": "D01", "name": "Dr. Adams", "shift_start": 0, "shift_end": 120 }
  ],
  "patients": [
    { "id": "P01", "arrival_time": 0, "visit_length": 30, "urgency": 1, "group": "private" }
  ]
}
```

Validation: unique patient and provider ids, every `patient.group` listed in
`meta.groups`, `shift_end > shift_start`.

## Input: `SimulationRequest`

```json
{
  "dataset": { "...": "Dataset as above" },
  "policies": ["fifo", "sjf", "urgency", "wspt", "optimal"],
  "weights": { "urgency_power": 2.0, "group_multipliers": { "uninsured": 1.5 }, "aging_rate": 0.05 },
  "top_k": 3
}
```

`weight(p, t) = urgency ** urgency_power * group_multipliers.get(group, 1) + aging_rate * (t - arrival_time)`

| Policy | Serves next (smallest key) |
|---|---|
| `fifo` | earliest arrival |
| `sjf` | shortest `visit_length` |
| `urgency` | highest `urgency` |
| `wspt` | highest `weight / visit_length` |
| `optimal` | brute force over all orders, minimizing (unserved, total weighted wait); ≤ 8 patients |

## Output: `SimulationResponse`

```json
{
  "schema_version": "1.0",
  "dataset_name": "tiny",
  "weights": { "...": "echo of the request" },
  "results": [
    {
      "policy": "fifo",
      "schedule": {
        "policy": "fifo",
        "appointments": [
          { "patient_id": "P01", "provider_id": "D01", "start": 0, "end": 30, "wait": 0, "order": 0 }
        ],
        "unserved": []
      },
      "metrics": {
        "served": 6, "unserved": 0, "makespan": 75, "total_weighted_wait": 983.7,
        "provider_utilization": { "D01": 0.625, "D02": 0.375 },
        "waits": { "count": 6, "mean": 9.7, "median": 10.0, "p90": 20.0, "max": 20,
                   "top_k": [{ "patient_id": "P05", "wait": 20 }] },
        "fairness": { "n": 6, "inversions_vs_arrival": 0, "inversions_vs_urgency": 8,
                      "disagreement_vs_arrival": 0.0, "disagreement_vs_urgency": 0.53 },
        "per_group": [
          { "group": "private", "served": 2, "unserved": 0, "waits": { "...": "" }, "fairness": { "...": "" } }
        ]
      },
      "engine": { "scheduler": "reference", "analytics": "reference" },
      "runtime_ms": 0.4
    }
  ]
}
```

### Metric definitions

* `order`: rank of the appointment by `(start, provider_id)`.
* `median`: the middle value, or the mean of the two middle values when n is even.
* `p90`: nearest rank, the ⌈0.9·n⌉-th smallest wait.
* `top_k`: longest waits descending, ties by `patient_id`.
* Wait stats cover served patients only (all zeros if nobody was served).
* **Fairness:** the service order is the served patients by `order`, then
  unserved patients in arrival order. Compare it against the reference ranking:
  * arrival: by `(arrival_time, id)`
  * urgency: by `(-urgency, arrival_time, id)`
  * `inversions_*` counts pairs served in the opposite order to the reference.
  * `disagreement_* = inversions / (n(n-1)/2)`.
  * Per-group fairness restricts both orders to that group's patients.
* `total_weighted_wait = Σ weight(p, start) · wait` over served patients.
* `provider_utilization = busy minutes / shift minutes`.

## Benchmarks: `BenchmarkRecord[]`

`backend/benchmarks/results/latest.json`:

```json
[{ "task": "median", "algorithm": "dselect", "n": 10000, "trials": 3, "mean_ms": 4.2, "min_ms": 4.0 }]
```

## Sample datasets (`data/samples/`)

| Name | Patients | Providers | Purpose |
|---|---|---|---|
| `tiny` | 6 | 2 | Hand-written; checkable by hand; works with `optimal` |
| `small` | 30 | 4 | Quick runs (~85% load, 4-hour day) |
| `medium` | 200 | 12 | Typical demo size (~95% load) |
| `overloaded` | 45 | 2 | ~130% load, so policies must choose who goes unserved |

Regenerate with `python -m scripts.make_sample_data` (from `backend/`). Put
throwaway datasets in `data/generated/`, which git ignores.
