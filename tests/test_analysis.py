import json

import numpy as np
import pandas as pd
import pytest

from satorl.analysis import analyze, correlation, pca_projection, summary_stats


def test_summary_stats_values():
    s = summary_stats(pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0]}))["a"]
    assert s["count"] == 4
    assert s["mean"] == 1.5
    assert s["min"] == 0.0
    assert s["max"] == 3.0
    assert s["p50"] == 1.5
    assert set(s) == {"count", "mean", "std", "min", "p25", "p50", "p75", "max"}


def test_summary_stats_skips_non_numeric():
    df = pd.DataFrame({"a": [1, 2, 3], "label": ["x", "y", "z"]})
    assert set(summary_stats(df)) == {"a"}


def test_correlation_identical_and_constant():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [2.0, 4.0, 6.0], "c": [5.0, 5.0, 5.0]})
    m = correlation(df)
    assert len(m) == 3 and all(len(row) == 3 for row in m)
    assert m[0][1] == pytest.approx(1.0)   # a vs b perfectly correlated
    assert m[2][2] is None                 # constant column -> NaN -> None


def test_pca_projection_shape_and_evr():
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.normal(size=(100, 5)), columns=[f"f{i}" for i in range(5)])
    proj = pca_projection(df, n_components=3)
    assert proj["method"] == "pca"
    assert proj["n_components"] == 3
    assert len(proj["coords"]) == 100
    assert all(len(row) == 3 for row in proj["coords"])
    assert len(proj["explained_variance_ratio"]) == 3
    assert sum(proj["explained_variance_ratio"]) <= 1.0 + 1e-9


def test_pca_clamps_components_to_features():
    df = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "b": [1.0, 0.0, 1.0, 0.0]})
    proj = pca_projection(df, n_components=3)   # only 2 features
    assert proj["n_components"] == 2
    assert all(len(row) == 2 for row in proj["coords"])


def test_analyze_full_shape():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [3.0, 2.0, 1.0], "label": ["x", "y", "z"]})
    result = analyze(df)
    assert result["shape"] == {"rows": 3, "cols": 3}
    assert result["columns"] == ["a", "b"]
    assert result["non_numeric_columns"] == ["label"]
    assert set(result) == {"shape", "columns", "non_numeric_columns", "summary", "correlation", "projection"}
    assert result["projection"]["method"] == "pca"


def test_analyze_rejects_unknown_projection():
    with pytest.raises(ValueError):
        analyze(pd.DataFrame({"a": [1.0, 2.0, 3.0]}), projection="bogus")


def test_umap_tsne_registered():
    from satorl.analysis import _PROJECTIONS
    assert {"umap", "tsne"} <= set(_PROJECTIONS)


def test_analyze_is_json_safe_with_nans():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": [0.0, 0.0, 0.0]})
    text = json.dumps(analyze(df))   # must not raise
    assert "NaN" not in text
