import typer

from satorl.cli.commands import generate
from satorl.cli.commands.analyze import analyze_command

app = typer.Typer(
    name="satorl",
    help="Generate synthetic datasets and upload them to S3.",
    no_args_is_help=True,   # base `satorl` prints help instead of erroring
    add_completion=False,
)

app.add_typer(generate.app, name="generate")
app.command("analyze")(analyze_command)

if __name__ == "__main__":      # lets you run `python -m satorl.cli.main` while developing
    app()
