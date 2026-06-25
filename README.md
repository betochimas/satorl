# satorl

Synthetic data generator and analysis CLI. Generate distribution-based datasets, write them to
local disk or S3 (each CSV gets a `*.meta.json` provenance sidecar), and analyze any CSV — summary
statistics, correlation, and a PCA projection — from the command line or a small FastAPI service.

## Install

```bash
pip install -e .          # core: generate + analyze + local/S3 storage
pip install -e ".[dev]"   # + pytest, coverage, moto, ruff
pip install -e ".[api]"   # + FastAPI service with UMAP / t-SNE projections
```

## Usage

```bash
# Generate Gaussian data -> out.csv + out.meta.json sidecar
satorl generate gaussian -n 1000 -c 3 -o out.csv
satorl generate gaussian -n 1000 -o s3://my-bucket/data/out.csv

# Analyze a CSV -> JSON (summary stats, correlation, PCA projection)
satorl analyze out.csv -k 3
```

## Analysis service

`satorl.analysis.analyze()` backs both the `satorl analyze` command and a FastAPI `/analyze`
endpoint (`satorl/api/app.py`), deployed to Cloud Run and called by the web visualizer for UMAP/t-SNE
projections and larger files. Run it locally with:

```bash
uvicorn satorl.api.app:app --reload
```
