from __future__ import annotations

from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_datasets_and_simulate():
    names = client.get("/api/datasets").json()
    assert "tiny" in names
    ds = client.get("/api/datasets/tiny").json()
    r = client.post("/api/simulate", json={"dataset": ds, "policies": ["fifo", "wspt", "optimal"]})
    assert r.status_code == 200, r.text
    assert [x["policy"] for x in r.json()["results"]] == ["fifo", "wspt", "optimal"]


def test_optimal_rejected_for_large_dataset():
    ds = client.get("/api/datasets/medium").json()
    assert client.post("/api/simulate", json={"dataset": ds, "policies": ["optimal"]}).status_code == 422


def test_generate():
    r = client.post("/api/datasets/generate", json={"n_patients": 20, "n_providers": 2})
    assert r.status_code == 200
    assert len(r.json()["patients"]) == 20


def test_unknown_dataset():
    assert client.get("/api/datasets/nope").status_code == 404
