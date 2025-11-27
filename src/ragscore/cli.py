import typer
from typing_extensions import Annotated

from .pipeline import run_pipeline

app = typer.Typer(
    name="ragscore",
    help="A CLI for generating QA datasets to evaluate RAG systems."
)

@app.command()
def generate(
    force_reindex: Annotated[bool, typer.Option("--force-reindex", "-f", help="Force re-reading and re-indexing of all documents in the data directory.")] = False
):
    """Run the full pipeline to generate a QA dataset from your documents."""
    try:
        run_pipeline(force_reindex=force_reindex)
    except Exception as e:
        typer.secho(f"An error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
