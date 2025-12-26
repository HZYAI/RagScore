import typer

app = typer.Typer(
    name="ragscore",
    help="Generate QA datasets to evaluate RAG systems.",
    add_completion=False,
)


@app.command("generate")
def generate(
    force_reindex: bool = typer.Option(
        False, "--force-reindex", "-f",
        help="Force re-reading and re-indexing of all documents."
    ),
):
    """Run the full pipeline to generate a QA dataset from your documents."""
    from .pipeline import run_pipeline
    
    try:
        run_pipeline(force_reindex=force_reindex)
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
