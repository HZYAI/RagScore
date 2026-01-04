from typing import Optional

import typer

HELP_TEXT = """
RAGScore Generate - QA Pair Generation for RAG & Fine-Tuning
Privacy-first, works with local LLMs or cloud providers

Note: This is RAGScore Generate (free, open source)
      Pro features & evaluation coming soon!

🚀 QUICK START (Copy-Paste Ready):
  # 1. Set API key (or use local Ollama)
  export OPENAI_API_KEY="sk-your-key-here"
  
  # 2. Generate QA pairs
  ragscore generate document.pdf
  
  # 3. Output saved to: output/generated_qas.jsonl

📚 COMMON COMMANDS:
  ragscore generate file.pdf           # Single file
  ragscore generate *.pdf              # Multiple files  
  ragscore generate ./docs/            # Directory

🔧 SUPPORTED LLMS (Auto-detected):
  ✅ OpenAI (set OPENAI_API_KEY)
  ✅ Anthropic (set ANTHROPIC_API_KEY)
  ✅ Ollama (runs locally, free - no key needed)
  ✅ DashScope, Groq, Together, DeepSeek

💡 TIPS:
  - Press Ctrl+C anytime to save progress
  - Use Ollama for free local generation
  - Supports PDF, TXT, MD, and more

� TROUBLESHOOTING:
  Error: "No API key"     → Set OPENAI_API_KEY or install Ollama
  Error: "NLTK data"      → Auto-downloads on first run
  Error: "File not found" → Check file path

📖 Docs: https://github.com/HZYAI/RagScore#readme
💬 Issues: https://github.com/HZYAI/RagScore/issues
⭐ Star: https://github.com/HZYAI/RagScore
"""

app = typer.Typer(
    name="ragscore",
    help=HELP_TEXT,
    add_completion=False,
    rich_markup_mode="markdown",
)


@app.command("generate")
def generate(
    paths: Optional[list[str]] = typer.Argument(
        None, help="Files or directories to process. If not provided, uses data/docs/"
    ),
    docs_dir: Optional[str] = typer.Option(
        None, "--docs-dir", "-d", help="[DEPRECATED] Use positional arguments instead"
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

      2. Run with your documents:
         ragscore generate paper.pdf           # Single file
         ragscore generate *.pdf               # Multiple files
         ragscore generate ./docs/             # Directory

    \b
    Examples:
      ragscore generate                        # Use default data/docs/
      ragscore generate paper.pdf              # Process single file
      ragscore generate file1.pdf file2.txt    # Process multiple files
      ragscore generate ./my_docs/             # Process directory

    \b
    Output:
      Generated QA pairs saved to: output/generated_qas.jsonl

    \b
    Need help? https://github.com/HZYAI/RagScore
    """

    from .pipeline import run_pipeline

    # Handle deprecated --docs-dir option
    if docs_dir:
        typer.secho(
            "⚠️  Warning: --docs-dir is deprecated. Use: ragscore generate /path/to/docs",
            fg=typer.colors.YELLOW,
        )
        paths = [docs_dir]

    try:
        run_pipeline(paths=paths)
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
