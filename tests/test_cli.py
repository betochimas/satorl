# End-to-End CLI via Typer's CliRunner
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