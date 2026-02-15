"""
RAGScore MCP Server

Exposes RAGScore functionality to AI assistants via Model Context Protocol (MCP).

Usage:
    # Run the server
    ragscore serve

    # Or directly
    python -m ragscore.mcp_server

Configuration (claude_desktop_config.json):
    {
      "mcpServers": {
        "ragscore": {
          "command": "ragscore",
          "args": ["serve"]
        }
      }
    }
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Check if MCP is available
try:
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    FastMCP = None


def _detect_provider_info(provider: str = None, model: str = None) -> str:
    """Return a short string describing which provider/model will be used."""
    from .providers import get_provider

    try:
        p = get_provider(provider=provider, model=model)
        key_env = None
        from .providers.factory import PROVIDER_ENV_KEYS

        key_env = PROVIDER_ENV_KEYS.get(p.provider_name)
        if key_env:
            import os

            masked = os.getenv(key_env, "")
            masked = f"{masked[:4]}...{masked[-4:]}" if len(masked) > 8 else "***"
            return f"🔑 Using: {p.provider_name} ({p.model}) [key: {key_env}={masked}]"
        return f"🔑 Using: {p.provider_name} ({p.model}) [no API key needed]"
    except Exception as e:
        return f"⚠️ No provider detected: {e}"


def create_mcp_server():
    """Create and configure the MCP server."""
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP not installed. Install with: pip install mcp\nOr: pip install ragscore[mcp]"
        )

    mcp = FastMCP("RAGScore")

    @mcp.tool()
    async def generate_qa_dataset(
        path: str,
        concurrency: int = 5,
        num_questions: int = 5,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate QA pairs from documents for RAG evaluation.

        Scans documents (PDF, TXT, MD) and generates question-answer pairs
        that can be used to test RAG systems.

        Args:
            path: Path to file or directory containing documents
            concurrency: Max concurrent LLM calls (default: 5)
            num_questions: Number of QA pairs to generate per chunk (default: 5)
            provider: LLM provider (openai, anthropic, ollama). Auto-detected if not set.
            model: LLM model name (e.g. gpt-4o-mini, claude-3-haiku). Uses provider default if not set.

        Returns:
            Summary of generation results and path to output file
        """
        from . import config
        from .data_processing import chunk_text, initialize_nltk
        from .pipeline import _async_generate_qas, _read_from_paths
        from .providers import get_provider

        # Suppress stdout for MCP (it uses stdout for communication)
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            config.ensure_dirs()
            initialize_nltk()

            docs = _read_from_paths([path])
            if not docs:
                return "❌ No documents found."

            all_chunks = []
            for doc in docs:
                chunks = chunk_text(doc["text"])
                for chunk_text_content in chunks:
                    if len(chunk_text_content.split()) >= 40:
                        all_chunks.append(
                            {
                                "doc_id": doc["doc_id"],
                                "path": doc["path"],
                                "text": chunk_text_content,
                                "chunk_id": len(all_chunks),
                            }
                        )

            if not all_chunks:
                return "❌ No valid chunks found (all too short)."

            llm_provider = get_provider(provider=provider, model=model)
            provider_info = _detect_provider_info(provider=provider, model=model)
            if llm_provider.provider_name == "ollama" and concurrency > 2:
                concurrency = 2

            all_qas = await _async_generate_qas(
                all_chunks,
                concurrency=concurrency,
                provider=llm_provider,
                num_questions=num_questions,
            )

            if not all_qas:
                return f"{provider_info}\n❌ No QA pairs were generated."

            output_file = str(config.GENERATED_QAS_PATH)
            with open(output_file, "w", encoding="utf-8") as f:
                for qa in all_qas:
                    f.write(json.dumps(qa, ensure_ascii=False) + "\n")

            return f"{provider_info}\n✅ Generated {len(all_qas)} QA pairs. Saved to: {output_file}"
        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            sys.stdout = old_stdout

    @mcp.tool()
    async def evaluate_rag(
        endpoint: str,
        dataset_path: Optional[str] = None,
        concurrency: int = 5,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        detailed: bool = False,
    ) -> str:
        """
        Evaluate a RAG API endpoint against a QA dataset.

        Queries the RAG endpoint with questions and scores the answers
        using LLM-as-judge (1-5 scale).

        Args:
            endpoint: RAG API endpoint URL (e.g., http://localhost:8000/query)
            dataset_path: Path to QA dataset JSONL (default: output/generated_qas.jsonl)
            concurrency: Max concurrent requests (default: 5)
            provider: LLM provider for judging (openai, anthropic, ollama). Auto-detected if not set.
            model: LLM model for judging (e.g. gpt-4o-mini). Uses provider default if not set.
            detailed: Enable multi-metric evaluation (correctness, completeness, relevance, conciseness, faithfulness). Default: False.

        Returns:
            Evaluation summary with accuracy and incorrect pairs
        """
        from . import config
        from .evaluation import RAGClient, load_golden_qas
        from .evaluation import evaluate_rag as _evaluate_rag
        from .providers import get_provider

        if dataset_path is None:
            dataset_path = str(config.GENERATED_QAS_PATH)

        # Suppress stdout for MCP
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            golden_qas = load_golden_qas(dataset_path)
            rag_client = RAGClient(endpoint=endpoint)
            llm_provider = get_provider(provider=provider, model=model)
            provider_info = _detect_provider_info(provider=provider, model=model)

            summary = await _evaluate_rag(
                golden_qas=golden_qas,
                rag_client=rag_client,
                provider=llm_provider,
                concurrency=concurrency,
                detailed=detailed,
            )

            result = f"""{provider_info}

📊 RAG Evaluation Results:
- Accuracy: {summary.accuracy:.1%} ({summary.correct}/{summary.total} correct)
- Average Score: {summary.avg_score:.1f}/5.0

"""
            if detailed and summary.results:
                metrics = [
                    "correctness",
                    "completeness",
                    "relevance",
                    "conciseness",
                    "faithfulness",
                ]
                for metric in metrics:
                    vals = [
                        getattr(r, metric)
                        for r in summary.results
                        if getattr(r, metric, None) is not None
                    ]
                    if vals:
                        avg = sum(vals) / len(vals)
                        label = metric.replace("_", " ").title()
                        result += f"- {label}: {avg:.1f}/5.0\n"
                result += "\n"

            if summary.incorrect > 0:
                result += f"❌ {summary.incorrect} incorrect answers found.\n"
                # Show first 3 failures
                incorrect = [r for r in summary.results if not r.is_correct][:3]
                for r in incorrect:
                    result += f"\nQ: {r.question[:80]}...\n"
                    result += f"   Score: {r.score}/5 - {r.reason}\n"
            else:
                result += "✅ All answers correct!"

            return result
        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            sys.stdout = old_stdout

    @mcp.tool()
    async def quick_test_rag(
        endpoint: str,
        docs_path: str,
        num_questions: int = 10,
        threshold: float = 0.7,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        detailed: bool = False,
    ) -> str:
        """
        Quick RAG accuracy test - generate QAs and evaluate in one call.

        Perfect for rapid iteration and sanity checks.

        Args:
            endpoint: RAG API endpoint URL
            docs_path: Path to documents to generate test questions from
            num_questions: Number of test questions (default: 10)
            threshold: Pass/fail accuracy threshold (default: 0.7 = 70%)
            provider: LLM provider (openai, anthropic, ollama). Auto-detected if not set.
            model: LLM model name. Uses provider default if not set.
            detailed: Enable multi-metric evaluation (correctness, completeness, relevance, conciseness, faithfulness). Default: False.

        Returns:
            Test results with pass/fail status and details
        """
        from . import config
        from .providers import get_provider
        from .quick_test import _quick_test_async

        # Suppress stdout for MCP
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            qt_provider = get_provider(model=model) if model else None
            provider_info = _detect_provider_info(model=model)

            result = await _quick_test_async(
                endpoint=endpoint,
                docs=docs_path,
                n=num_questions,
                threshold=threshold,
                concurrency=5,
                silent=True,
                provider=qt_provider,
                judge_provider=qt_provider,
                detailed=detailed,
            )

            # Save corrections so get_corrections() can retrieve them
            if result.corrections:
                corrections_path = Path(config.OUTPUT_DIR) / "quick_test_corrections.jsonl"
                with open(corrections_path, "w") as f:
                    for c in result.corrections:
                        f.write(json.dumps(c, ensure_ascii=False) + "\n")

            status = "✅ PASSED" if result.passed else "❌ FAILED"
            output = f"""{provider_info}

{status}

📊 Quick Test Results:
- Accuracy: {result.accuracy:.0%} ({result.correct}/{result.total} correct)
- Average Score: {result.avg_score:.1f}/5.0
- Threshold: {threshold:.0%}

"""
            if detailed and result.details:
                metrics = [
                    "correctness",
                    "completeness",
                    "relevance",
                    "conciseness",
                    "faithfulness",
                ]
                for metric in metrics:
                    vals = [d.get(metric) for d in result.details if d.get(metric) is not None]
                    if vals:
                        avg = sum(vals) / len(vals)
                        label = metric.replace("_", " ").title()
                        output += f"- {label}: {avg:.1f}/5.0\n"
                output += "\n"

            if result.corrections:
                output += f"🔧 {len(result.corrections)} corrections available.\n"
                output += "Use get_corrections() to retrieve them.\n"

            return output
        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            sys.stdout = old_stdout

    @mcp.tool()
    async def get_corrections(
        output_path: Optional[str] = None,
    ) -> str:
        """
        Get corrections from the last quick test for RAG improvement.

        Returns incorrect QA pairs that can be injected into the RAG
        system to improve accuracy.

        Args:
            output_path: Optional path to save corrections JSONL

        Returns:
            JSON array of corrections or path to saved file
        """
        from . import config

        results_path = Path(config.OUTPUT_DIR) / "quick_test_corrections.jsonl"

        if not results_path.exists():
            return "No corrections available. Run quick_test_rag first."

        corrections = []
        with open(results_path) as f:
            for line in f:
                if line.strip():
                    corrections.append(json.loads(line))

        if output_path:
            with open(output_path, "w") as f:
                for c in corrections:
                    f.write(json.dumps(c, ensure_ascii=False) + "\n")
            return f"✅ Saved {len(corrections)} corrections to: {output_path}"

        return json.dumps(corrections, indent=2, ensure_ascii=False)

    @mcp.resource("ragscore://latest_results")
    def get_latest_results() -> str:
        """Returns the full JSON content of the last evaluation run."""
        from . import config

        results_path = Path(config.OUTPUT_DIR) / "results.json"
        if results_path.exists():
            return results_path.read_text()
        return '{"error": "No results available. Run evaluate_rag first."}'

    @mcp.resource("ragscore://generated_qas")
    def get_generated_qas() -> str:
        """Returns the generated QA pairs from the last generation run."""
        from . import config

        if config.GENERATED_QAS_PATH.exists():
            lines = config.GENERATED_QAS_PATH.read_text().strip().split("\n")
            qas = [json.loads(line) for line in lines if line.strip()]
            return json.dumps(qas[:100], indent=2, ensure_ascii=False)  # Limit to 100
        return '{"error": "No QA pairs available. Run generate_qa_dataset first."}'

    return mcp


def run_server():
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP not installed. Install with: pip install mcp", file=sys.stderr)
        print("Or: pip install ragscore[mcp]", file=sys.stderr)
        sys.exit(1)

    print("RAGScore MCP Server starting...", file=sys.stderr)
    print(_detect_provider_info(), file=sys.stderr)

    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    run_server()
