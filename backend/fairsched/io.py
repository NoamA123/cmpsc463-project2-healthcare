from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from fairsched.schema import Dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "data" / "samples"


def load_dataset(path: str | Path) -> Dataset:
    return Dataset.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_json(model: BaseModel, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")


def list_samples() -> list[str]:
    return sorted(p.stem for p in SAMPLES_DIR.glob("*.json"))
