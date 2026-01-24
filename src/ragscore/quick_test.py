"""
RAGScore Quick Test Module

Fast, notebook-friendly RAG evaluation in a single function call.
Generates QA pairs and evaluates RAG in one pipeline.

Returns a "Rich Object" with metrics, DataFrame, and visualization.

Usage:
    from ragscore import quick_test

    # 1. Audit your RAG in one line
    result = quick_test("http://localhost:8000/query", docs="docs/")

    # 2. See the report
    result.plot()

    # 3. Inspect failures
    bad_rows = result.df[result.df['score'] < 3]
    display(bad_rows[['question', 'rag_answer', 'reason']])
"""

import asyncio
import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Union

from .data_processing import chunk_text, initialize_nltk
from .exceptions import RAGScoreError
from .llm import agenerate_qa_for_chunk, detect_language, safe_json_parse
from .ui import get_async_pbar, patch_asyncio


@dataclass
class QuickTestResult:
    """
    Result of a quick RAG test.

    The "Rich Object" pattern - contains data, DataFrame, and visualization.

    Usage:
        result = quick_test(endpoint, docs="docs/")

        # Access metrics
        print(f"Accuracy: {result.accuracy:.1%}")

        # Access DataFrame
        result.df.head()
        bad_rows = result.df[result.df['score'] < 3]

        # Visualize
        result.plot()
    """

    total: int = 0
    correct: int = 0
    accuracy: float = 0.0
    avg_score: float = 0.0
    passed: bool = False
    threshold: float = 0.7
    details: list[dict] = field(default_factory=list)
    corrections: list[dict] = field(default_factory=list)

    def __repr__(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"QuickTestResult({status}: {self.correct}/{self.total} correct, {self.accuracy:.0%} accuracy)"

    @property
    def df(self):
        """
        Results as a pandas DataFrame.

        Columns: question, golden_answer, rag_answer, score, reason, is_correct, source
        """
        try:
            import pandas as pd

            return pd.DataFrame(self.details)
        except ImportError as e:
            raise ImportError(
                "pandas is required for .df property. Install with: pip install pandas"
            ) from e

    def plot(self, figsize: tuple = (12, 4)):
        """
        Generate a 3-panel visualization of the test results.

        Panel 1: Pass/Fail pie chart (Is it good?)
        Panel 2: Score distribution histogram (How good?)
        Panel 3: Corrections count (What to fix?)

        Args:
            figsize: Figure size tuple (width, height)
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("⚠️ Plotting requires matplotlib. Install with: pip install matplotlib")
            return

        fig, axes = plt.subplots(1, 3, figsize=figsize)

        # Panel 1: Pass/Fail Pie Chart
        if self.correct > 0 or self.total - self.correct > 0:
            axes[0].pie(
                [self.correct, self.total - self.correct],
                labels=["Correct", "Incorrect"],
                colors=["#4CAF50", "#f44336"],
                autopct="%1.0f%%",
                startangle=90,
            )
        axes[0].set_title(
            f"Accuracy: {self.accuracy:.0%}\n({'PASSED' if self.passed else 'FAILED'} @ {self.threshold:.0%} threshold)"
        )

        # Panel 2: Score Distribution
        if self.details:
            scores = [d.get("score", 0) for d in self.details]
            axes[1].hist(
                scores,
                bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                edgecolor="black",
                color="#2196F3",
                rwidth=0.8,
            )
            axes[1].set_xlabel("Score")
            axes[1].set_ylabel("Count")
            axes[1].set_xticks([1, 2, 3, 4, 5])
        axes[1].set_title(f"Score Distribution\n(avg: {self.avg_score:.1f}/5.0)")

        # Panel 3: Corrections Summary
        axes[2].axis("off")
        n_corrections = len(self.corrections)
        if n_corrections > 0:
            axes[2].text(
                0.5,
                0.6,
                f"{n_corrections}",
                ha="center",
                va="center",
                fontsize=48,
                fontweight="bold",
                color="#f44336",
            )
            axes[2].text(
                0.5, 0.3, "corrections needed", ha="center", va="center", fontsize=14, color="#666"
            )
        else:
            axes[2].text(0.5, 0.5, "✓", ha="center", va="center", fontsize=64, color="#4CAF50")
            axes[2].text(
                0.5,
                0.2,
                "No corrections needed",
                ha="center",
                va="center",
                fontsize=12,
                color="#666",
            )
        axes[2].set_title("Items to Fix")

        plt.tight_layout()
        plt.show()

        return fig

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total": self.total,
            "correct": self.correct,
            "accuracy": round(self.accuracy, 4),
            "avg_score": round(self.avg_score, 2),
            "passed": self.passed,
            "threshold": self.threshold,
            "details": self.details,
            "corrections": self.corrections,
        }

    def to_dataframe(self):
        """Deprecated: Use .df property instead."""
        return self.df


def _read_docs_for_quicktest(docs: Union[str, list[str], Path]) -> list[dict]:
    """Read documents from path(s) for quick test."""
    import uuid

    import PyPDF2

    if isinstance(docs, (str, Path)):
        docs = [str(docs)]

    all_docs = []
    files_to_process = []

    for path_str in docs:
        path = Path(path_str)
        if not path.exists():
            continue

        if path.is_file():
            files_to_process.append(path)
        elif path.is_dir():
            supported = (".pdf", ".txt", ".md", ".html")
            files_to_process.extend([p for p in path.rglob("*") if p.suffix.lower() in supported])

    for file_path in files_to_process:
        text = ""
        try:
            if file_path.suffix.lower() == ".pdf":
                with open(file_path, "rb") as fh:
                    reader = PyPDF2.PdfReader(fh)
                    text = "".join(page.extract_text() or "" for page in reader.pages)
            else:
                with open(file_path, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()

            if text.strip():
                all_docs.append({"doc_id": str(uuid.uuid4()), "path": str(file_path), "text": text})
        except Exception:
            continue

    return all_docs


def _build_judge_prompt(question: str, golden_answer: str, rag_answer: str, lang: str) -> str:
    """Build the LLM-as-judge prompt."""
    if lang == "zh":
        return f"""比较RAG系统的回答与标准答案。

问题: {question}
标准答案: {golden_answer}
RAG回答: {rag_answer}

评分标准 (1-5分):
- 5: 完全正确，语义等价
- 4: 基本正确，有轻微遗漏
- 3: 部分正确，有一些错误
- 2: 大部分错误，有重大问题
- 1: 完全错误或无关

请输出JSON格式: {{"score": 分数, "reason": "简短解释"}}"""
    else:
        return f"""Compare the RAG answer to the golden answer for this question.

Question: {question}
Golden Answer: {golden_answer}
RAG Answer: {rag_answer}

Score 1-5:
- 5: Fully correct, semantically equivalent
- 4: Mostly correct, minor omissions
- 3: Partially correct, some errors
- 2: Mostly incorrect, major errors
- 1: Completely wrong or irrelevant

Output JSON: {{"score": N, "reason": "brief explanation"}}"""


async def _quick_test_async(
    endpoint: Union[str, Callable],
    docs: Union[str, list[str], Path],
    n: int = 10,
    threshold: float = 0.7,
    concurrency: int = 5,
    silent: bool = False,
    provider=None,
    judge_provider=None,
) -> QuickTestResult:
    """Async implementation of quick_test."""
    import aiohttp

    # Get providers
    if provider is None:
        from .providers import get_provider

        provider = get_provider()

    if judge_provider is None:
        judge_provider = provider

    # Initialize NLTK
    initialize_nltk()

    # Read and chunk documents
    all_docs = _read_docs_for_quicktest(docs)
    if not all_docs:
        raise RAGScoreError(f"No documents found in {docs}")

    all_chunks = []
    for doc in all_docs:
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
        raise RAGScoreError("No valid chunks found (all too short)")

    # Sample chunks for quick test
    sample_chunks = random.sample(all_chunks, min(n, len(all_chunks)))

    semaphore = asyncio.Semaphore(concurrency)
    results = []
    corrections = []

    # Determine if endpoint is a function or URL
    is_function = callable(endpoint)

    async def process_chunk(chunk: dict) -> Optional[dict]:
        """Generate QA, query RAG, and judge - all in one."""
        async with semaphore:
            try:
                # 1. Generate QA pair
                difficulty = random.choice(["easy", "medium", "hard"])
                qas = await agenerate_qa_for_chunk(
                    chunk["text"], difficulty, n=1, provider=provider
                )
                if not qas:
                    return None

                qa = qas[0]
                question = qa.get("question", "")
                golden_answer = qa.get("answer", "")

                if not question or not golden_answer:
                    return None

                # 2. Query RAG endpoint
                if is_function and callable(endpoint):
                    # Call function directly
                    try:
                        if asyncio.iscoroutinefunction(endpoint):
                            rag_answer = await endpoint(question)
                        else:
                            rag_answer = endpoint(question)
                        rag_answer = str(rag_answer) if rag_answer else ""
                    except Exception as e:
                        rag_answer = f"[ERROR: {e}]"
                else:
                    # HTTP endpoint
                    async with aiohttp.ClientSession() as session:
                        try:
                            payload = {"question": question}
                            async with session.post(
                                endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                            ) as response:
                                data = await response.json()
                                rag_answer = data.get(
                                    "answer", data.get("response", data.get("text", ""))
                                )
                                rag_answer = str(rag_answer) if rag_answer else ""
                        except Exception as e:
                            rag_answer = f"[ERROR: {e}]"

                # 3. Judge the answer
                lang = detect_language(question)
                judge_prompt = _build_judge_prompt(question, golden_answer, rag_answer, lang)

                messages = [
                    {
                        "role": "system",
                        "content": "You are an impartial judge. Output only valid JSON.",
                    },
                    {"role": "user", "content": judge_prompt},
                ]

                try:
                    response = await judge_provider.agenerate(
                        messages=messages, temperature=0.3, json_mode=True
                    )
                    data = safe_json_parse(response.content)
                    score = max(1, min(5, int(data.get("score", 1))))
                    reason = data.get("reason", "No reason provided")
                except Exception as e:
                    score = 1
                    reason = f"Judge error: {e}"

                is_correct = score >= 4

                result = {
                    "question": question,
                    "golden_answer": golden_answer,
                    "rag_answer": rag_answer,
                    "score": score,
                    "reason": reason,
                    "is_correct": is_correct,
                    "source": chunk["path"],
                }

                # Track corrections for incorrect answers
                if not is_correct:
                    corrections.append(
                        {
                            "question": question,
                            "incorrect_answer": rag_answer,
                            "correct_answer": golden_answer,
                            "source": chunk["path"],
                        }
                    )

                return result

            except Exception as e:
                if not silent:
                    print(f"Error processing chunk: {e}", file=sys.stderr)
                return None

    # Process all chunks
    tasks = [process_chunk(chunk) for chunk in sample_chunks]

    if silent:
        raw_results = await asyncio.gather(*tasks)
    else:
        async_pbar = get_async_pbar()
        raw_results = await async_pbar.gather(*tasks, desc="Quick Testing")

    # Filter out None results
    results = [r for r in raw_results if r is not None]

    if not results:
        return QuickTestResult(
            total=0,
            correct=0,
            accuracy=0.0,
            avg_score=0.0,
            passed=False,
            threshold=threshold,
            details=[],
            corrections=[],
        )

    # Calculate summary
    total = len(results)
    correct = sum(1 for r in results if r["is_correct"])
    accuracy = correct / total if total > 0 else 0.0
    avg_score = sum(r["score"] for r in results) / total if total > 0 else 0.0
    passed = accuracy >= threshold

    return QuickTestResult(
        total=total,
        correct=correct,
        accuracy=accuracy,
        avg_score=avg_score,
        passed=passed,
        threshold=threshold,
        details=results,
        corrections=corrections,
    )


def quick_test(
    endpoint: Union[str, Callable],
    docs: Union[str, list[str], Path],
    n: int = 10,
    threshold: float = 0.7,
    concurrency: int = 5,
    silent: bool = False,
    model: Optional[str] = None,
    judge_model: Optional[str] = None,
) -> QuickTestResult:
    """
    Quick RAG accuracy test - generate QAs and evaluate in one call.

    Returns a Rich Object with metrics, DataFrame, and visualization.
    Perfect for notebooks, CI/CD, and rapid iteration.

    Args:
        endpoint: RAG API URL (str) or callable function
        docs: Path to documents (file, directory, or list of paths)
        n: Number of test questions to generate (default: 10)
        threshold: Pass/fail accuracy threshold (default: 0.7 = 70%)
        concurrency: Max concurrent operations (default: 5)
        silent: Suppress progress output (default: False)
        model: LLM model for QA generation (auto-detected if None)
        judge_model: LLM model for judging (uses model if None)

    Returns:
        QuickTestResult - Rich Object with:
            - .accuracy, .total, .correct, .passed - metrics
            - .df - pandas DataFrame of all results
            - .plot() - 3-panel visualization
            - .corrections - list of items to fix

    Examples:
        # Basic usage
        result = quick_test("http://localhost:8000/query", docs="docs/")
        print(f"Accuracy: {result.accuracy:.0%}")

        # Access DataFrame
        result.df.head()
        bad_rows = result.df[result.df['score'] < 3]

        # Visualize results
        result.plot()

        # With a function (no server needed)
        def my_rag(question):
            return my_vectorstore.query(question)
        result = quick_test(my_rag, docs="docs/")

        # In pytest
        def test_rag_accuracy():
            result = quick_test(endpoint, docs="docs/", threshold=0.8)
            assert result.passed, f"RAG accuracy too low: {result.accuracy:.0%}"
    """
    # Get providers
    provider = None
    judge_provider = None

    if model or judge_model:
        from .providers import get_provider

        if model:
            provider = get_provider(model=model)
        if judge_model:
            judge_provider = get_provider(model=judge_model)

    # Patch asyncio for notebook environments
    patch_asyncio()

    # Run async function
    result = asyncio.run(
        _quick_test_async(
            endpoint=endpoint,
            docs=docs,
            n=n,
            threshold=threshold,
            concurrency=concurrency,
            silent=silent,
            provider=provider,
            judge_provider=judge_provider,
        )
    )

    # Print summary unless silent
    if not silent:
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\n{'=' * 50}")
        print(f"{status}: {result.correct}/{result.total} correct ({result.accuracy:.0%})")
        print(f"Average Score: {result.avg_score:.1f}/5.0")
        print(f"Threshold: {threshold:.0%}")
        print(f"{'=' * 50}")

        if result.corrections:
            print(f"\n❌ {len(result.corrections)} incorrect answers found.")
            print("Use result.df to inspect, result.plot() to visualize.")

    return result


def export_corrections(
    result: QuickTestResult,
    output_path: Union[str, Path] = "corrections.jsonl",
) -> str:
    """
    Export corrections from a QuickTestResult to JSONL file.

    These corrections can be injected into your RAG system to improve accuracy.

    Args:
        result: QuickTestResult from quick_test()
        output_path: Path to save corrections JSONL

    Returns:
        Path to the saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for correction in result.corrections:
            f.write(json.dumps(correction, ensure_ascii=False) + "\n")

    return str(output_path)
