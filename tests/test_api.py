import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from satorl.api.app import app  # noqa: E402

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_pca():
    csv = "a,b\n1,2\n3,4\n5,6\n7,8\n"
    r = client.post(
        "/analyze",
        params={"projection": "pca", "n_components": 2},
        files={"file": ("d.csv", csv, "text/csv")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["columns"] == ["a", "b"]
    assert body["projection"]["method"] == "pca"
    assert body["projection"]["n_components"] == 2


def test_analyze_rejects_unparseable_csv():
    r = client.post("/analyze", files={"file": ("empty.csv", "", "text/csv")})
    assert r.status_code == 400


def test_analyze_rejects_oversize(monkeypatch):
    import satorl.api.app as api

    monkeypatch.setattr(api, "MAX_BYTES", 4)
    r = client.post("/analyze", files={"file": ("d.csv", "a,b\n1,2\n3,4\n", "text/csv")})
    assert r.status_code == 413
