from typing import Optional

import typer

app = typer.Typer(
    name="ragscore",
    help="Generate high-quality QA datasets to evaluate RAG systems.",
    add_completion=False,
)


@app.command("generate")
def generate(
    docs_dir: Optional[str] = typer.Option(
        None, "--docs-dir", "-d", help="Path to directory containing PDF/TXT/MD documents"
    ),
    force_reindex: bool = typer.Option(
        False, "--force-reindex", "-f", help="Force re-reading and re-indexing of all documents"
    ),
):
    """
    Generate QA pairs from your documents.

    \b
    Quick Start:
      1. Set your API key:
         export OPENAI_API_KEY="sk-..."        # For OpenAI
         export DASHSCOPE_API_KEY="sk-..."     # For DashScope/Qwen
         export ANTHROPIC_API_KEY="sk-..."     # For Claude

      2. Place documents in data/docs/ folder

      3. Run: ragscore generate

    \b
    Examples:
      ragscore generate                        # Use default data/docs/
      ragscore generate -d /path/to/docs       # Custom directory
      ragscore generate -f                     # Force re-index

    \b
    Output:
      Generated QA pairs saved to: output/generated_qas.jsonl

    \b
    Need help? https://github.com/HZYAI/RagScore
    """
    from pathlib import Path

    from .pipeline import run_pipeline

    # Convert docs_dir to Path if provided
    docs_path = Path(docs_dir) if docs_dir else None

    try:
        run_pipeline(docs_dir=docs_path, force_reindex=force_reindex)
    except ValueError as e:
        typer.secho(f"\n❌ Configuration error: {e}", fg=typer.colors.RED)
        typer.secho("\n💡 Tip: Set your API key with:", fg=typer.colors.YELLOW)
        typer.secho("   export OPENAI_API_KEY='your-key-here'", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1) from None
    except Exception as e:
        typer.secho(f"\n❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
):
    """
    RAGScore - Generate QA datasets to evaluate RAG systems.

    \b
    🚀 Quick Start:
      1. Install: pip install ragscore[openai]
      2. Set API key: export OPENAI_API_KEY="sk-..."
      3. Add docs to: data/docs/
      4. Run: ragscore generate

    \b
    📚 Documentation: https://github.com/HZYAI/RagScore
    """
    if version:
        from . import __version__

        typer.echo(f"RAGScore version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
