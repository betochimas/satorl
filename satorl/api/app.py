import io
import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from satorl.analysis import analyze

MAX_BYTES = 5 * 1024 * 1024  # ~5 MB; the client handles smaller files itself (locked cap)

logger = logging.getLogger("satorl.api")


def _warm_projections() -> None:
    """Pay the umap/numba + t-SNE import & JIT-compile cost at startup, not on the first
    user request. Best-effort: never blocks startup — if the [api] extra isn't installed,
    the per-request lazy import returns a 503 instead."""
    try:
        import numpy as np
        import umap
        from sklearn.manifold import TSNE

        warm = np.random.default_rng(0).normal(size=(20, 4))
        umap.UMAP(n_components=2, n_neighbors=5).fit_transform(warm)
        TSNE(n_components=2, perplexity=5.0, init="pca").fit_transform(warm)
        logger.info("projection warmup complete (umap, tsne)")
    except Exception as exc:
        logger.info("projection warmup skipped: %s", exc)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _warm_projections()
    yield


app = FastAPI(title="satorl analysis API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                   # Vite dev
        "https://dylanchimasanchez.com",
        "https://www.dylanchimasanchez.com",
    ],
    allow_origin_regex=r"https://.*\.pages\.dev",   # Cloudflare Pages previews
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_endpoint(
    file: UploadFile = File(...),
    projection: str = Query("pca", pattern="^(pca|umap|tsne)$"),
    n_components: int = Query(3, ge=2, le=3),
    standardize: bool = Query(True),
) -> dict:
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_BYTES} bytes.")
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc
    try:
        return analyze(df, projection=projection, n_components=n_components, standardize=standardize)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportError as exc:                       # umap/tsne extra not installed on the server
        raise HTTPException(status_code=503, detail=str(exc)) from exc
