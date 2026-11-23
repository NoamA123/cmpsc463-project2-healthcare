"""Runtime benchmarks: selection vs sorting, merge-count vs O(n^2) inversions. Owner: Yony.

    cd backend
    python -m scripts.run_benchmarks

Writes a list of BenchmarkRecord to benchmarks/results/latest.json.
Algorithms that still raise NotImplementedError are skipped.
"""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Callable

from pydantic import TypeAdapter

from fairsched.analytics import baselines, inversions, selection
from fairsched.schema import BenchmarkRecord

RESULTS = Path(__file__).resolve().parents[1] / "benchmarks" / "results" / "latest.json"
SIZES = [1_000, 10_000, 100_000]
BRUTE_FORCE_MAX_N = 5_000
TRIALS = 3


def _time(fn: Callable[[], object], trials: int) -> list[float]:
    out = []
    for _ in range(trials):
        t0 = time.perf_counter()
        fn()
        out.append((time.perf_counter() - t0) * 1000)
    return out


def main() -> None:
    rng = random.Random(0)
    records: list[BenchmarkRecord] = []
    for n in SIZES:
        xs = [rng.randrange(10 * n) for _ in range(n)]
        perm = rng.sample(range(n), n)
        cases: list[tuple[str, str, Callable[[], object]]] = [
            ("median", "sort", lambda: baselines.sort_median(xs)),
            ("median", "rselect", lambda: selection.median(xs, method="rselect")),
            ("median", "dselect", lambda: selection.median(xs, method="dselect")),
            ("inversions", "merge_count", lambda: inversions.count_inversions(perm)),
        ]
        if n <= BRUTE_FORCE_MAX_N:
            cases.append(("inversions", "brute_force", lambda: baselines.brute_force_inversions(perm)))
        for task, algo, fn in cases:
            try:
                times = _time(fn, TRIALS)
            except NotImplementedError:
                print(f"skip {task}/{algo} (not implemented)")
                continue
            rec = BenchmarkRecord(task=task, algorithm=algo, n=n, trials=TRIALS, mean_ms=sum(times) / TRIALS, min_ms=min(times))
            records.append(rec)
            print(f"{task:>10} {algo:>12} n={n:>7}  mean={rec.mean_ms:9.2f} ms")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_bytes(TypeAdapter(list[BenchmarkRecord]).dump_json(records, indent=2))
    print(f"wrote {RESULTS.relative_to(RESULTS.parents[2])}")


if __name__ == "__main__":
    main()
