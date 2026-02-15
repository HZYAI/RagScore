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

_DETAILED_METRICS = [
    "correctness",
    "completeness",
    "relevance",
    "conciseness",
    "faithfulness",
]


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

    def plot(self, figsize: tuple = None):
        """
        Generate a visualization of the test results.

        Default (3-panel): Pass/Fail pie, Score histogram, Corrections count.
        Detailed (4-panel): Adds a radar chart of multi-metric averages.

        Args:
            figsize: Figure size tuple (width, height). Auto-sized if None.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("⚠️ Plotting requires matplotlib. Install with: pip install matplotlib")
            return

        # Check if detailed metrics are available
        has_detailed = self.details and any(d.get("correctness") is not None for d in self.details)
        n_panels = 4 if has_detailed else 3
        if figsize is None:
            figsize = (16, 4) if has_detailed else (12, 4)

        fig, axes = plt.subplots(1, n_panels, figsize=figsize)

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

        # Panel 3 (detailed only): Radar Chart of Metrics
        if has_detailed:
            axes[2].remove()
            ax_radar = fig.add_subplot(1, n_panels, 3, polar=True)
            metrics = _DETAILED_METRICS
            labels = [m.replace("_", " ").title() for m in metrics]
            avgs = []
            for m in metrics:
                vals = [d.get(m) for d in self.details if d.get(m) is not None]
                avgs.append(sum(vals) / len(vals) if vals else 0)

            # Radar chart
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            avgs_plot = avgs + [avgs[0]]
            angles += [angles[0]]

            ax_radar.set_theta_offset(np.pi / 2)
            ax_radar.set_theta_direction(-1)
            ax_radar.plot(angles, avgs_plot, "o-", linewidth=2, color="#2196F3")
            ax_radar.fill(angles, avgs_plot, alpha=0.25, color="#2196F3")
            ax_radar.set_xticks(angles[:-1])
            ax_radar.set_xticklabels(labels, size=8)
            ax_radar.set_ylim(0, 5)
            ax_radar.set_yticks([1, 2, 3, 4, 5])
            ax_radar.set_yticklabels(["1", "2", "3", "4", "5"], size=7)
            ax_radar.set_title("Detailed Metrics", pad=20)

        # Last Panel: Corrections Summary
        ax_corr = axes[-1]
        ax_corr.axis("off")
        n_corrections = len(self.corrections)
        if n_corrections > 0:
            ax_corr.text(
                0.5,
                0.6,
                f"{n_corrections}",
                ha="center",
                va="center",
                fontsize=48,
                fontweight="bold",
                color="#f44336",
            )
            ax_corr.text(
                0.5, 0.3, "corrections needed", ha="center", va="center", fontsize=14, color="#666"
            )
        else:
            ax_corr.text(0.5, 0.5, "✓", ha="center", va="center", fontsize=64, color="#4CAF50")
            ax_corr.text(
                0.5,
                0.2,
                "No corrections needed",
                ha="center",
                va="center",
                fontsize=12,
                color="#666",
            )
        ax_corr.set_title("Items to Fix")

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


def _build_judge_prompt(
    question: str, golden_answer: str, rag_answer: str, lang: str, detailed: bool = False
) -> str:
    """Build the LLM-as-judge prompt."""
    if detailed:
        return _build_detailed_judge_prompt(question, golden_answer, rag_answer, lang)

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


def _build_detailed_judge_prompt(
    question: str, golden_answer: str, rag_answer: str, lang: str
) -> str:
    """Build the detailed multi-metric LLM-as-judge prompt."""
    if lang == "zh":
        return f"""你是一个公正的评审，对RAG系统的回答进行多维度评估。

问题: {question}
标准答案: {golden_answer}
RAG回答: {rag_answer}

请从以下5个维度评分 (每项1-5分):

1. correctness (正确性): 回答与标准答案的语义一致程度
   5=完全正确 4=基本正确 3=部分正确 2=大部分错误 1=完全错误

2. completeness (完整性): 回答是否涵盖了标准答案中的所有关键信息
   5=完全覆盖 4=轻微遗漏 3=遗漏部分要点 2=遗漏大量信息 1=几乎未覆盖

3. relevance (相关性): 回答是否针对所提问题
   5=完全切题 4=基本切题 3=部分偏题 2=大部分偏题 1=完全无关

4. conciseness (简洁性): 回答是否简洁，没有多余或无关的信息
   5=简洁精准 4=略有冗余 3=有明显冗余 2=大量无关内容 1=完全冗余

5. faithfulness (忠实度): 回答是否忠实于标准答案中的信息，没有编造内容
   5=完全忠实 4=基本忠实 3=有一些不确定内容 2=有明显编造信息 1=大量编造信息

请输出JSON格式:
{{"score": 综合分数, "reason": "简短解释", "correctness": 分数, "completeness": 分数, "relevance": 分数, "conciseness": 分数, "faithfulness": 分数}}"""
    else:
        return f"""You are an impartial judge evaluating a RAG system answer across multiple dimensions.

Question: {question}
Golden Answer: {golden_answer}
RAG Answer: {rag_answer}

Score each dimension 1-5:

1. correctness: How semantically close is the answer to the golden answer?
   5=Fully correct  4=Mostly correct  3=Partially correct  2=Mostly wrong  1=Completely wrong

2. completeness: Does the answer cover all key points from the golden answer?
   5=Fully covered  4=Minor omissions  3=Some key points missing  2=Major gaps  1=Almost nothing covered

3. relevance: Does the answer actually address the question asked?
   5=Perfectly on-topic  4=Mostly on-topic  3=Partially off-topic  2=Mostly off-topic  1=Completely irrelevant

4. conciseness: Is the answer focused without unnecessary or irrelevant information?
   5=Concise and precise  4=Slightly verbose  3=Noticeably verbose  2=Mostly filler  1=Entirely off-track

5. faithfulness: Is the answer faithful to the golden answer without fabricating information?
   5=Fully faithful  4=Mostly faithful  3=Some unsupported claims  2=Significant fabrication  1=Mostly fabricated

Output JSON: {{"score": N, "reason": "brief explanation", "correctness": N, "completeness": N, "relevance": N, "conciseness": N, "faithfulness": N}}"""


async def _quick_test_async(
    endpoint: Union[str, Callable],
    docs: Union[str, list[str], Path],
    n: int = 10,
    threshold: float = 0.7,
    concurrency: int = 5,
    silent: bool = False,
    provider=None,
    judge_provider=None,
    detailed: bool = False,
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

    async def process_chunk(
        chunk: dict, http_session: Optional[aiohttp.ClientSession] = None
    ) -> Optional[dict]:
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
                    # HTTP endpoint - use shared session
                    try:
                        payload = {"question": question}
                        async with http_session.post(
                            endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                        ) as resp:
                            data = await resp.json()
                            rag_answer = data.get(
                                "answer", data.get("response", data.get("text", ""))
                            )
                            rag_answer = str(rag_answer) if rag_answer else ""
                    except Exception as e:
                        rag_answer = f"[ERROR: {e}]"

                # 3. Judge the answer
                lang = detect_language(question)
                judge_prompt = _build_judge_prompt(
                    question, golden_answer, rag_answer, lang, detailed=detailed
                )

                messages = [
                    {
                        "role": "system",
                        "content": "You are an impartial judge. Output only valid JSON.",
                    },
                    {"role": "user", "content": judge_prompt},
                ]

                try:
                    judge_resp = await judge_provider.agenerate(
                        messages=messages, temperature=0.3, json_mode=True
                    )
                    data = safe_json_parse(judge_resp.content)
                    score = max(1, min(5, int(data.get("score", 1))))
                    reason = data.get("reason", "No reason provided")
                except Exception as e:
                    score = 1
                    reason = f"Judge error: {e}"
                    data = {}

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

                # Add detailed metrics if available
                if detailed:
                    for metric in _DETAILED_METRICS:
                        val = data.get(metric)
                        if val is not None:
                            result[metric] = max(1, min(5, int(val)))
                        else:
                            result[metric] = None

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

    # Process all chunks with a shared HTTP session
    async with aiohttp.ClientSession() as shared_session:
        tasks = [process_chunk(chunk, http_session=shared_session) for chunk in sample_chunks]

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
    detailed: bool = False,
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
        detailed: Enable multi-metric evaluation (correctness, completeness,
                  relevance, conciseness, hallucination_risk) (default: False)

    Returns:
        QuickTestResult - Rich Object with:
            - .accuracy, .total, .correct, .passed - metrics
            - .df - pandas DataFrame of all results
            - .plot() - 3-panel visualization (5-panel when detailed=True)
            - .corrections - list of items to fix

    Examples:
        # Basic usage
        result = quick_test("http://localhost:8000/query", docs="docs/")
        print(f"Accuracy: {result.accuracy:.0%}")

        # Detailed multi-metric evaluation
        result = quick_test(endpoint, docs="docs/", detailed=True)
        result.df[["question", "correctness", "completeness", "faithfulness"]]

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
            detailed=detailed,
        )
    )

    # Print summary unless silent
    if not silent:
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\n{'=' * 50}")
        print(f"{status}: {result.correct}/{result.total} correct ({result.accuracy:.0%})")
        print(f"Average Score: {result.avg_score:.1f}/5.0")
        print(f"Threshold: {threshold:.0%}")

        if detailed and result.details:
            separator = "─" * 50
            print(separator)
            for metric in _DETAILED_METRICS:
                vals = [d.get(metric) for d in result.details if d.get(metric) is not None]
                if vals:
                    avg = sum(vals) / len(vals)
                    label = metric.replace("_", " ").title()
                    print(f"  {label}: {avg:.1f}/5.0")

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
