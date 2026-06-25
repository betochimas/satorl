import os
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version

import pandas as pd

from satorl.generators.base import Generator

SCHEMA_VERSION = 1

def _satorl_version() -> str:
    try:
        return version("satorl")
    except PackageNotFoundError:
        return "0.0.0+unknown"

def build_metadata(generator: Generator, df: pd.DataFrame) -> dict:
    """Assemble the `*.meta.json` sidecar contents for a generated dataset."""
    return {
        "satorl_version": _satorl_version(),
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": {
            "name": generator.name,
            "params": generator.params(),
            "seed": generator.seed
        },
        "data": {
            "rows": int(len(df)),
            "columns": [str(c) for c in df.columns],
            "dtypes": {str(c): str(t) for c, t in df.dtypes.items()}
        },
    }

def meta_path_for(destination: str) -> str:
    """`out.csv` -> `out.meta.json`; `s3://b/k/out.csv` -> `s3://b/k/out.meta.json`
    Assumes a single-extension data file (splits on the last dot after the last slash).
    """
    root, _ext = os.path.splitext(destination)
    return f"{root}.meta.json"