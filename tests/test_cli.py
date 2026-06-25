# End-to-End CLI via Typer's CliRunner
import json

import pandas as pd
from typer.testing import CliRunner

from satorl.cli.main import app

runner = CliRunner()

def test_generate_writes_local_csv(tmp_path):
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", "gaussian", "-n", "10", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert sum(1 for _ in out.open()) == 11     # header + 10 rows

def test_generate_rejects_zero_rows(tmp_path):
    result = runner.invoke(app, ["generate", "gaussian", "-n", "0", "-o", str(tmp_path / "x.csv")])
    assert result.exit_code != 0                # --rows min=1 validation (Click exits 2)

def test_generate_writes_sidecar_by_default(tmp_path):
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", "gaussian", "-n", "10", "-o", str(out)])
    assert result.exit_code == 0
    meta = tmp_path / "out.meta.json"
    assert meta.exists()
    loaded = json.loads(meta.read_text())
    assert loaded["data"]["rows"] == 10
    assert loaded["generator"]["name"] == "gaussian"

def test_generate_no_meta_skips_sidecar(tmp_path):
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", "gaussian", "-n", "10", "-o", str(out), "--no-meta"])
    assert result.exit_code == 0
    assert out.exists()
    assert not (tmp_path / "out.meta.json").exists()

def test_generate_to_s3_writes_csv_and_sidecar(s3_client):   # s3_client fixture = moto
    result = runner.invoke(app, ["generate", "gaussian", "-n", "5", "-o", "s3://test-bucket/data/out.csv"])
    assert result.exit_code == 0
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket="test-bucket").get("Contents", [])}
    assert "data/out.csv" in keys
    assert "data/out.meta.json" in keys

def test_analyze_outputs_json(tmp_path):
    csv = tmp_path / "data.csv"
    pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [3.0, 2.0, 1.0]}).to_csv(csv, index=False)
    result = runner.invoke(app, ["analyze", str(csv)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["columns"] == ["a", "b"]
    assert payload["projection"]["method"] == "pca"

def test_analyze_components_option(tmp_path):
    csv = tmp_path / "data.csv"
    pd.DataFrame(
        {"a": [1.0, 2.0, 3.0, 4.0], "b": [4.0, 3.0, 2.0, 1.0], "c": [1.0, 0.0, 1.0, 0.0]}
    ).to_csv(csv, index=False)
    result = runner.invoke(app, ["analyze", str(csv), "-k", "2"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["projection"]["n_components"] == 2