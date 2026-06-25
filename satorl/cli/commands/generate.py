import json
from typing import Optional

import typer

from satorl.generators.base import Generator
from satorl.generators.gaussian import GaussianGenerator
from satorl.metadata import build_metadata, meta_path_for
from satorl.storage import open_destination

app = typer.Typer(no_args_is_help=True, help="Generate a dataset with a chosen generator.")

@app.command("gaussian")
def gaussian(
    output: str = typer.Option(..., "--output", "-o", help="Destination: s3://bucket/key.csv or a local path like ./out.csv"),
    rows: int = typer.Option(1000, "--rows", "-n", min=1, help="Number of rows."),
    columns: int = typer.Option(3, "--columns", "-c", min=1, help="Number of feature columns."),
    mean: float = typer.Option(0.0, help="Mean of the normal distribution."),
    std: float = typer.Option(1.0, min=0.0, help="Standard deviation."),
    seed: Optional[int] = typer.Option(None, help="Random seed for reproducible output."),
    meta: bool = typer.Option(True, "--meta/--no-meta", help="Also write a <name>.meta.json sidecar."),
) -> None:
    """Generate normally-distributed numeric data."""
    generator = GaussianGenerator(columns=columns, mean=mean, std=std, seed=seed)
    _run(generator, rows=rows, output=output, meta=meta)

def _run(generator: Generator, *, rows: int, output: str, meta: bool) -> None:
    """Shared generate -> store pipeline. Knows only the abstract interfaces."""
    df = generator.generate(rows)
    storage = open_destination(output)
    location = storage.write(df, output)
    if meta:
        meta_dest = meta_path_for(output)
        storage.write_text(json.dumps(build_metadata(generator, df), indent=2), meta_dest)
        typer.secho(f"  + metadata -> {meta_dest}", fg=typer.colors.BLUE)
        typer.secho(
            f"Wrote {len(df):,} rows x {len(df.columns)} cols to {location}",
            fg=typer.colors.GREEN,
        )