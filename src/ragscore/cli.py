from typing import Optional

import typer

HELP_TEXT = """
RAGScore - Generate QA datasets & evaluate RAG systems in 2 commands

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 2-LINE RAG EVALUATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ragscore generate docs/                         # Step 1: Generate QAs
  ragscore evaluate http://localhost:8000/query   # Step 2: Evaluate RAG

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  generate <paths>     Generate QA pairs from documents (PDF, TXT, MD)
  evaluate <endpoint>  Evaluate RAG system against golden QA pairs
  serve                Start MCP server for AI assistant integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 SUPPORTED LLMS (auto-detected):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Ollama     ollama serve                    (local, free, private)
  OpenAI     export OPENAI_API_KEY="sk-..."  (best quality)
  Anthropic  export ANTHROPIC_API_KEY="..."  (long context)
  DashScope  export DASHSCOPE_API_KEY="..."  (Qwen models)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ragscore generate paper.pdf                 # Single file
  ragscore generate docs/*.pdf -c 10          # Batch with concurrency
  ragscore evaluate http://api/query          # Evaluate RAG
  ragscore evaluate http://api/query -o out.json  # Save results

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI ASSISTANT INTEGRATION (MCP):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ragscore serve                              # Start MCP server
  # Then add to Claude Desktop config to use RAGScore from Claude!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 LINKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Docs:    https://github.com/HZYAI/RagScore
  Issues:  https://github.com/HZYAI/RagScore/issues
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
    concurrency: int = typer.Option(
        5,
        "--concurrency",
        "-c",
        help="Max concurrent LLM calls (default: 5, use 10-20 for local LLMs)",
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
        run_pipeline(paths=paths, concurrency=concurrency)
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


@app.command("serve")
def serve():
    """
    Start the RAGScore MCP server for AI assistant integration.

    \b
    This allows AI assistants (Claude Desktop, Cursor, etc.) to use
    RAGScore tools directly via the Model Context Protocol (MCP).

    \b
    Setup for Claude Desktop:
      Add to ~/Library/Application Support/Claude/claude_desktop_config.json:

      {
        "mcpServers": {
          "ragscore": {
            "command": "ragscore",
            "args": ["serve"]
          }
        }
      }

    \b
    Requires: pip install ragscore[mcp]
    """
    try:
        from .mcp_server import run_server

        run_server()
    except ImportError:
        typer.secho(
            "\n❌ MCP not installed. Install with: pip install ragscore[mcp]",
            fg=typer.colors.RED,
        )
        typer.secho("   Or: pip install mcp", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1) from None


@app.command("evaluate")
def evaluate(
    endpoint: str = typer.Argument(
        ..., help="RAG API endpoint URL (e.g., http://localhost:8000/query)"
    ),
    golden: Optional[str] = typer.Option(
        None, "--golden", "-g", help="Path to golden QA pairs (default: output/generated_qas.jsonl)"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save results to JSON file (optional)"
    ),
    concurrency: int = typer.Option(
        5, "--concurrency", "-c", help="Max concurrent requests (default: 5)"
    ),
    question_field: str = typer.Option(
        "question", "--question-field", help="Field name for question in RAG request"
    ),
    answer_field: str = typer.Option(
        "answer", "--answer-field", help="Field name for answer in RAG response"
    ),
    method: str = typer.Option("POST", "--method", "-m", help="HTTP method (POST or GET)"),
    model: Optional[str] = typer.Option(
        None, "--model", help="LLM model for judging (e.g., gpt-4o, claude-3-sonnet)"
    ),
):
    """
    Evaluate your RAG system against golden QA pairs.

    \b
    Usage:
      ragscore evaluate http://localhost:8000/query

    \b
    This will:
      1. Load QA pairs from output/generated_qas.jsonl (or --golden path)
      2. Query your RAG endpoint with each question
      3. Score answers using LLM-as-judge (1-5 scale)
      4. Show results + incorrect pairs in terminal
    """
    from . import config
    from .evaluation import run_evaluation

    # Default golden path to generated QAs
    if golden is None:
        golden = str(config.GENERATED_QAS_PATH)

    try:
        run_evaluation(
            golden_path=golden,
            endpoint=endpoint,
            output_path=output,
            concurrency=concurrency,
            question_field=question_field,
            answer_field=answer_field,
            method=method,
            model=model,
        )
    except FileNotFoundError as e:
        typer.secho(f"\n❌ File not found: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None
    except ValueError as e:
        typer.secho(f"\n❌ Configuration error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from None
    except Exception as e:
        typer.secho(f"\n❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
