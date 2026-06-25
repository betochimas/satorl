import json

from satorl.generators.gaussian import GaussianGenerator
from satorl.metadata import build_metadata, meta_path_for


def test_meta_path_for_local():
    assert meta_path_for("out.csv") == "out.meta.json"
    assert meta_path_for("data/sub/out.csv") == "data/sub/out.meta.json"
    assert meta_path_for("noext") == "noext.meta.json"


def test_meta_path_for_s3():
    assert meta_path_for("s3://bucket/k/out.csv") == "s3://bucket/k/out.meta.json"


def test_build_metadata_shape():
    gen = GaussianGenerator(columns=3, mean=0.0, std=1.0, seed=42)
    meta = build_metadata(gen, gen.generate(10))

    assert meta["schema_version"] == 1
    assert meta["created_at"].endswith("Z")
    assert meta["generator"]["name"] == "gaussian"
    assert meta["generator"]["params"] == {"columns": 3, "mean": 0.0, "std": 1.0}
    assert meta["generator"]["seed"] == 42
    assert meta["data"]["rows"] == 10
    assert meta["data"]["columns"] == [f"feature_{i}" for i in range(3)]
    assert set(meta["data"]["dtypes"]) == set(meta["data"]["columns"])


def test_build_metadata_seed_none():
    gen = GaussianGenerator(seed=None)
    assert build_metadata(gen, gen.generate(5))["generator"]["seed"] is None


def test_metadata_is_json_serializable():
    gen = GaussianGenerator(seed=1)
    json.dumps(build_metadata(gen, gen.generate(5)))  # must not raise
