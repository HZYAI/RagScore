import typer

app = typer.Typer(
    name="ragscore",
    help="Generate QA datasets to evaluate RAG systems.",
    add_completion=False,
)


@app.command("generate")
def generate(
    docs_dir: str = typer.Option(
        None, "--docs-dir", "-d",
        help="Path to directory containing documents (default: ./data/docs)"
    ),
    force_reindex: bool = typer.Option(
        False, "--force-reindex", "-f",
        help="Force re-reading and re-indexing of all documents."
    ),
):
    """Run the full pipeline to generate a QA dataset from your documents."""
    from pathlib import Path
    from .pipeline import run_pipeline
    
    # Convert docs_dir to Path if provided
    docs_path = Path(docs_dir) if docs_dir else None
    
    try:
        run_pipeline(
            docs_dir=docs_path,
            force_reindex=force_reindex
        )
    except ValueError as e:
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """RAGScore - Generate QA datasets to evaluate RAG systems."""
    if ctx.invoked_subcommand is None:
        # If no subcommand, show help
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
