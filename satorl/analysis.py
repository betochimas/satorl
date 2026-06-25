from typing import Any

import numpy as np
import pandas as pd

def _numeric(df: pd.DataFrame) -> pd.DataFrame:
    return df.select_dtypes(include="number")

def _safe(x: Any) -> float | None:
    """JSON-safe float: NaN/inf -> None, numpy float -> python float."""
    v = float(x)
    return None if (np.isnan(v) or np.isinf(v)) else v

def _prep(df: pd.DataFrame, standardize: bool) -> np.ndarray:
    """Numeric matrix with NaN rows dropped and (optionally) z-scored. Shared by all projections."""
    X = _numeric(df).to_numpy(dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    if standardize:
        mu = X.mean(axis=0)
        sd = X.std(axis=0)
        sd[sd == 0] = 1.0
        X = (X - mu) / sd
    return X

def summary_stats(df: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for col, s in _numeric(df).items():
        out[str(col)] = {
            "count": int(s.count()),
            "mean": _safe(s.mean()),
            "std": _safe(s.std()),
            "min": _safe(s.min()),
            "p25": _safe(s.quantile(0.25)),
            "p50": _safe(s.quantile(0.50)),
            "p75": _safe(s.quantile(0.75)),
            "max": _safe(s.max()),
        }
    return out

def correlation(df: pd.DataFrame) -> list[list[float | None]]:
    """Pearson correlation matrix over numeric columns; rows/cols aligned to them."""
    corr = _numeric(df).corr().to_numpy()
    return [[_safe(v) for v in row] for row in corr]

def pca_projection(df: pd.DataFrame, n_components: int = 3, standardize: bool = True) -> dict[str, Any]:
    """PCA via numpy SVD — no scikit-learn. (Standardization mean-centers regardless.)"""
    X = _prep(df, standardize)
    Xc = X - X.mean(axis=0)                      # center (no-op-ish if already standardized)
    k = max(1, min(n_components, Xc.shape[1], Xc.shape[0]))
    _U, S, _Vt = np.linalg.svd(Xc, full_matrices=False)
    coords = _U[:, :k] * S[:k]
    var = (S ** 2) / max(Xc.shape[0] - 1, 1)
    total = var.sum()
    evr = (var / total)[:k] if total else np.zeros(k)
    return {
        "method": "pca",
        "n_components": int(k),
        "coords": [[_safe(v) for v in row] for row in coords],
        "explained_variance_ratio": [_safe(v) for v in evr],
    }

_PROJECTIONS = {"pca": pca_projection}

def analyze(df: pd.DataFrame, *, projection: str = "pca",
            n_components: int = 3, standardize: bool = True) -> dict[str, Any]:
    """Assemble the function the CLI and API both call."""
    if projection not in _PROJECTIONS:
        raise ValueError(
            f"projection {projection!r} is not available in the core package "
            f"(have {sorted(_PROJECTIONS)}); umap/tsne require `pip install satorl[api]`."
        )
    numeric_cols = [str(c) for c in _numeric(df).columns]
    return {
        "shape": {"rows": int(len(df)), "cols": int(df.shape[1])},
        "columns": numeric_cols,
        "non_numeric_columns": [str(c) for c in df.columns if str(c) not in numeric_cols],
        "summary": summary_stats(df),
        "correlation": correlation(df),
        "projection": _PROJECTIONS[projection](df, n_components, standardize),
    }

def umap_projection(df: pd.DataFrame, n_components: int = 3, standardize: bool = True) -> dict[str, Any]:
    """UMAP projection — requires the [api] extra (umap-learn)."""
    try:
        import umap
    except ImportError as exc:
        raise ImportError("umap projection requires `pip install satorl[api]`") from exc
    coords = umap.UMAP(n_components=n_components).fit_transform(_prep(df, standardize))
    return {
        "method": "umap",
        "n_components": int(n_components),
        "coords": [[_safe(v) for v in row] for row in coords],
    }

def tsne_projection(df: pd.DataFrame, n_components: int = 3, standardize: bool = True) -> dict[str, Any]:
    """t-SNE projection — requires the [api] extra (scikit-learn)."""
    try:
        from sklearn.manifold import TSNE
    except ImportError as exc:
        raise ImportError("tsne projection requires `pip install satorl[api]`") from exc
    coords = TSNE(n_components=n_components, init="pca").fit_transform(_prep(df, standardize))
    return {
        "method": "tsne",
        "n_components": int(n_components),
        "coords": [[_safe(v) for v in row] for row in coords],
    }

_PROJECTIONS["umap"] = umap_projection
_PROJECTIONS["tsne"] = tsne_projection

