import json
from pathlib import Path

import pandas as pd
import typer

from satorl.analysis import analyze

def analyze_command(
        csv: Path = typer.Argument(..., exists=True, readable=True, help="CSV file to analyze."),
        output: str = typer.Option("-", "--output", "-o", help="Write JSON here; '-' = stdout."),
        components: int = typer.Option(3, "--components", "-k", min=2, max=3, help="Projection dimensions."),
        standardize: bool = typer.Option(True, "--standardize/--no-standardize", help="Z-score columns before PCA."),
) -> None:
    """Analyze a CSV: per-column stats, correlation, and a PCA projection."""
    result = analyze(pd.read_csv(csv), n_components=components, standardize=standardize)
    text = json.dumps(result, indent=2)
    if output == "-":
        typer.echo(text)
    else:
        Path(output).write_text(text)
        typer.secho(f"Wrote analysis to {output}", fg=typer.colors.GREEN)
