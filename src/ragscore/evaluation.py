"""
RAGScore Evaluation Module

Evaluates RAG system outputs against golden QA pairs using LLM-as-judge.
"""

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import aiohttp

from .exceptions import RAGScoreError
from .llm import detect_language, safe_json_parse
from .ui import get_async_pbar, patch_asyncio

_DETAILED_METRICS = [
    "correctness",
    "completeness",
    "relevance",
    "conciseness",
    "faithfulness",
]


@dataclass
class EvaluationResult:
    """Result of evaluating a single QA pair."""

    id: str
    question: str
    golden_answer: str
    rag_answer: str
    score: int  # 1-5
    reason: str
    is_correct: bool  # score >= 4
    correctness: Optional[int] = None
    completeness: Optional[int] = None
    relevance: Optional[int] = None
    conciseness: Optional[int] = None
    faithfulness: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "id": self.id,
            "question": self.question,
            "golden_answer": self.golden_answer,
            "rag_answer": self.rag_answer,
            "score": self.score,
            "reason": self.reason,
            "is_correct": self.is_correct,
        }
        for metric in _DETAILED_METRICS:
            val = getattr(self, metric, None)
            if val is not None:
                d[metric] = val
        return d


@dataclass
class EvaluationSummary:
    """Summary of evaluation results."""

    total: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy: float = 0.0
    avg_score: float = 0.0
    results: list[EvaluationResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        incorrect_pairs = [r.to_dict() for r in self.results if not r.is_correct]
        return {
            "summary": {
                "total": self.total,
                "correct": self.correct,
                "incorrect": self.incorrect,
                "accuracy": round(self.accuracy, 4),
                "avg_score": round(self.avg_score, 2),
            },
            "incorrect_pairs": incorrect_pairs,
        }


class RAGClient:
    """Client for calling RAG endpoints."""

    def __init__(
        self,
        endpoint: str,
        method: str = "POST",
        question_field: str = "question",
        answer_field: str = "answer",
        headers: Optional[dict[str, str]] = None,
        timeout: int = 30,
    ):
        """
        Initialize RAG client.

        Args:
            endpoint: RAG API endpoint URL
            method: HTTP method (POST or GET)
            question_field: Field name for question in request body
            answer_field: Field name for answer in response
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.method = method.upper()
        self.question_field = question_field
        self.answer_field = answer_field
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def query(self, question: str, session: aiohttp.ClientSession) -> str:
        """
        Query the RAG endpoint with a question.

        Args:
            question: The question to ask
            session: aiohttp session for connection pooling

        Returns:
            The RAG system's answer
        """
        try:
            if self.method == "POST":
                payload = {self.question_field: question}
                async with session.post(
                    self.endpoint, json=payload, headers=self.headers, timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
            else:  # GET
                params = {self.question_field: question}
                async with session.get(
                    self.endpoint, params=params, headers=self.headers, timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            # Extract answer from response
            answer = data.get(self.answer_field, "")
            if not answer and isinstance(data, dict):
                # Try common alternative field names
                for alt_field in ["response", "text", "content", "result"]:
                    if alt_field in data:
                        answer = data[alt_field]
                        break

            return str(answer) if answer else ""

        except aiohttp.ClientError as e:
            raise RAGScoreError(f"RAG endpoint error: {e}") from e
        except Exception as e:
            raise RAGScoreError(f"Failed to query RAG endpoint: {e}") from e


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


async def _judge_single(
    qa: dict[str, Any],
    rag_answer: str,
    provider,
    semaphore: asyncio.Semaphore,
    detailed: bool = False,
) -> EvaluationResult:
    """Judge a single QA pair."""
    question = qa.get("question", "")
    golden_answer = qa.get("answer", "")
    qa_id = qa.get("id", "unknown")

    # Detect language from question
    lang = detect_language(question)

    # Build judge prompt
    user_prompt = _build_judge_prompt(question, golden_answer, rag_answer, lang, detailed=detailed)

    system_prompt = (
        "You are an impartial judge evaluating RAG system answers. "
        "Be strict but fair. Output only valid JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    async with semaphore:
        try:
            response = await provider.agenerate(messages=messages, temperature=0.3, json_mode=True)
            data = safe_json_parse(response.content)
            score = int(data.get("score", 1))
            reason = data.get("reason", "No reason provided")
        except Exception as e:
            # Default to low score on error
            score = 1
            reason = f"Evaluation error: {e}"
            data = {}

    # Clamp score to valid range
    score = max(1, min(5, score))

    # Extract detailed metrics
    metric_kwargs = {}
    if detailed:
        for metric in _DETAILED_METRICS:
            val = data.get(metric)
            if val is not None:
                metric_kwargs[metric] = max(1, min(5, int(val)))

    return EvaluationResult(
        id=qa_id,
        question=question,
        golden_answer=golden_answer,
        rag_answer=rag_answer,
        score=score,
        reason=reason,
        is_correct=(score >= 4),
        **metric_kwargs,
    )


async def evaluate_rag(
    golden_qas: list[dict[str, Any]],
    rag_client: RAGClient,
    provider=None,
    concurrency: int = 5,
    correct_threshold: int = 4,
    detailed: bool = False,
) -> EvaluationSummary:
    """
    Evaluate RAG system against golden QA pairs.

    Args:
        golden_qas: List of golden QA pairs (must have 'question' and 'answer')
        rag_client: RAGClient instance for querying the RAG endpoint
        provider: LLM provider for judging (auto-detected if None)
        concurrency: Max concurrent requests (default: 5)
        correct_threshold: Score threshold for "correct" (default: 4)
        detailed: Enable multi-metric evaluation (default: False)

    Returns:
        EvaluationSummary with results and incorrect pairs
    """
    if provider is None:
        from .providers import get_provider

        provider = get_provider()

    semaphore = asyncio.Semaphore(concurrency)

    # Query RAG + Judge in single pipeline (parallel)
    async with aiohttp.ClientSession() as session:

        async def process_qa(qa: dict[str, Any]) -> EvaluationResult:
            question = qa.get("question", "")

            # Query RAG endpoint
            async with semaphore:
                try:
                    rag_answer = await rag_client.query(question, session)
                except Exception as e:
                    rag_answer = f"[ERROR: {e}]"

            # Immediately judge the answer
            return await _judge_single(qa, rag_answer, provider, semaphore, detailed=detailed)

        tasks = [process_qa(qa) for qa in golden_qas]
        async_pbar = get_async_pbar()
        results: list[EvaluationResult] = await async_pbar.gather(*tasks, desc="Evaluating")

    # Calculate summary
    total = len(results)
    correct = sum(1 for r in results if r.is_correct)
    incorrect = total - correct
    avg_score = sum(r.score for r in results) / total if total > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0

    return EvaluationSummary(
        total=total,
        correct=correct,
        incorrect=incorrect,
        accuracy=accuracy,
        avg_score=avg_score,
        results=results,
    )


def load_golden_qas(path: Union[str, Path]) -> list[dict[str, Any]]:
    """
    Load golden QA pairs from a JSONL file.

    Args:
        path: Path to JSONL file

    Returns:
        List of QA pair dictionaries
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Golden QA file not found: {path}")

    qas = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    qa = json.loads(line)
                    if "question" in qa and "answer" in qa:
                        qas.append(qa)
                except json.JSONDecodeError:
                    continue

    if not qas:
        raise ValueError(f"No valid QA pairs found in {path}")

    return qas


def run_evaluation(
    golden_path: Union[str, Path],
    endpoint: str,
    output_path: Optional[Union[str, Path]] = None,
    concurrency: int = 5,
    question_field: str = "question",
    answer_field: str = "answer",
    method: str = "POST",
    headers: Optional[dict[str, str]] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    detailed: bool = False,
) -> EvaluationSummary:
    """
    Run RAG evaluation pipeline (synchronous wrapper).

    Args:
        golden_path: Path to golden QA pairs JSONL file
        endpoint: RAG API endpoint URL
        output_path: Optional path to save results JSON
        concurrency: Max concurrent requests
        question_field: Field name for question in RAG request
        answer_field: Field name for answer in RAG response
        method: HTTP method (POST or GET)
        headers: Optional HTTP headers for RAG endpoint
        model: LLM model for judging (auto-detected if None)
        provider: LLM provider for judging (e.g., 'ollama', 'openai'). Auto-detected if None.
        detailed: Enable multi-metric evaluation (default: False)

    Returns:
        EvaluationSummary with results
    """
    # Load golden QAs
    print(f"Loading golden QA pairs from {golden_path}...")
    golden_qas = load_golden_qas(golden_path)
    print(f"Loaded {len(golden_qas)} QA pairs")

    # Create RAG client
    rag_client = RAGClient(
        endpoint=endpoint,
        method=method,
        question_field=question_field,
        answer_field=answer_field,
        headers=headers,
    )

    # Get LLM provider for judging
    from .providers import get_provider

    llm_provider = get_provider(provider=provider, model=model)

    # Patch asyncio for notebook environments
    patch_asyncio()

    # Run evaluation
    print(f"\nEvaluating against RAG endpoint: {endpoint}")
    print(f"Judge LLM: {llm_provider.provider_name} ({llm_provider.model})")
    print(f"Concurrency: {concurrency}")

    summary = asyncio.run(
        evaluate_rag(
            golden_qas=golden_qas,
            rag_client=rag_client,
            provider=llm_provider,
            concurrency=concurrency,
            detailed=detailed,
        )
    )

    # Print summary
    print(f"\n{'=' * 60}")
    if summary.accuracy >= 0.9:
        status = "✅ EXCELLENT"
    elif summary.accuracy >= 0.7:
        status = "👍 GOOD"
    elif summary.accuracy >= 0.5:
        status = "⚠️  NEEDS IMPROVEMENT"
    else:
        status = "❌ POOR"

    print(f"{status}: {summary.correct}/{summary.total} correct ({summary.accuracy * 100:.1f}%)")
    print(f"Average Score: {summary.avg_score:.2f}/5.0")

    if detailed and summary.results:
        separator = "\u2500" * 60
        print(separator)
        for metric in _DETAILED_METRICS:
            vals = [
                getattr(r, metric) for r in summary.results if getattr(r, metric, None) is not None
            ]
            if vals:
                avg = sum(vals) / len(vals)
                label = metric.replace("_", " ").title()
                print(f"  {label}: {avg:.2f}/5.0")

    print(f"{'=' * 60}")

    # Print incorrect pairs
    incorrect = [r for r in summary.results if not r.is_correct]
    if incorrect:
        print(f"\n❌ {len(incorrect)} Incorrect Pairs:\n")
        for i, r in enumerate(incorrect[:10], 1):  # Show first 10
            q_preview = r.question[:60] + "..." if len(r.question) > 60 else r.question
            print(f'  {i}. Q: "{q_preview}"')
            print(f"     Score: {r.score}/5 - {r.reason}")
            print()

        if len(incorrect) > 10:
            print(f"  ... and {len(incorrect) - 10} more (use --output to save all)")

    # Save results
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n📄 Full results saved to {output_path}")
    elif incorrect:
        print("💡 Tip: Use --output results.json to save all incorrect pairs")

    print("\n⭐ Enjoying RAGScore? Star us: https://github.com/HZYAI/RagScore")
    print("💬 Questions? Join discussions: https://github.com/HZYAI/RagScore/discussions")

    return summary
