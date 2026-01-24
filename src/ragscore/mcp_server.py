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
        num_questions: int = 50,
        concurrency: int = 5,
    ) -> str:
        """
        Generate QA pairs from documents for RAG evaluation.

        Scans documents (PDF, TXT, MD) and generates question-answer pairs
        that can be used to test RAG systems.

        Args:
            path: Path to file or directory containing documents
            num_questions: Approximate number of QA pairs to generate
            concurrency: Max concurrent LLM calls (default: 5)

        Returns:
            Summary of generation results and path to output file
        """
        from . import config
        from .pipeline import run_pipeline

        # Suppress stdout for MCP (it uses stdout for communication)
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            run_pipeline(paths=[path], concurrency=concurrency)
            output_path = str(config.GENERATED_QAS_PATH)

            # Count generated QAs
            count = 0
            if Path(output_path).exists():
                with open(output_path) as f:
                    count = sum(1 for _ in f)

            return f"✅ Generated {count} QA pairs. Saved to: {output_path}"
        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            sys.stdout = old_stdout

    @mcp.tool()
    async def evaluate_rag(
        endpoint: str,
        dataset_path: Optional[str] = None,
        concurrency: int = 5,
    ) -> str:
        """
        Evaluate a RAG API endpoint against a QA dataset.

        Queries the RAG endpoint with questions and scores the answers
        using LLM-as-judge (1-5 scale).

        Args:
            endpoint: RAG API endpoint URL (e.g., http://localhost:8000/query)
            dataset_path: Path to QA dataset JSONL (default: output/generated_qas.jsonl)
            concurrency: Max concurrent requests (default: 5)

        Returns:
            Evaluation summary with accuracy and incorrect pairs
        """
        from . import config
        from .evaluation import run_evaluation

        if dataset_path is None:
            dataset_path = str(config.GENERATED_QAS_PATH)

        # Suppress stdout for MCP
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            summary = run_evaluation(
                golden_path=dataset_path,
                endpoint=endpoint,
                concurrency=concurrency,
            )

            result = f"""📊 RAG Evaluation Results:
- Accuracy: {summary.accuracy:.1%} ({summary.correct}/{summary.total} correct)
- Average Score: {summary.avg_score:.1f}/5.0

"""
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
    ) -> str:
        """
        Quick RAG accuracy test - generate QAs and evaluate in one call.

        Perfect for rapid iteration and sanity checks.

        Args:
            endpoint: RAG API endpoint URL
            docs_path: Path to documents to generate test questions from
            num_questions: Number of test questions (default: 10)
            threshold: Pass/fail accuracy threshold (default: 0.7 = 70%)

        Returns:
            Test results with pass/fail status and details
        """
        from .quick_test import quick_test

        # Suppress stdout for MCP
        old_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            result = quick_test(
                endpoint=endpoint,
                docs=docs_path,
                n=num_questions,
                threshold=threshold,
                silent=True,
            )

            status = "✅ PASSED" if result.passed else "❌ FAILED"
            output = f"""{status}

📊 Quick Test Results:
- Accuracy: {result.accuracy:.0%} ({result.correct}/{result.total} correct)
- Average Score: {result.avg_score:.1f}/5.0
- Threshold: {threshold:.0%}

"""
            if result.corrections:
                output += f"🔧 {len(result.corrections)} corrections available.\n"
                output += "Use get_corrections() to retrieve them for injection.\n"

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

    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    run_server()
