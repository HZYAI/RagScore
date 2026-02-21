import json
import re
import uuid
from typing import Any


def safe_json_parse(raw: str) -> dict[str, Any]:
    """Safely parses a JSON string, cleaning and attempting to fix common errors."""
    if not raw:
        return {}

    # Clean control characters
    cleaned = re.sub(r"[\x00-\x1f]+", " ", raw)

    # Attempt to complete truncated JSON
    if cleaned.count("{") > cleaned.count("}"):
        cleaned += "}" * (cleaned.count("{") - cleaned.count("}"))
    if cleaned.count("[") > cleaned.count("]"):
        cleaned += "]" * (cleaned.count("[") - cleaned.count("]"))

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fix unescaped quotes inside JSON string values (common with Anthropic/Claude)
    # e.g. "rationale": "The context states that "RAGScore" is..." -> escaped inner quotes
    def _fix_inner_quotes(text: str) -> str:
        result = []
        i = 0
        in_string = False
        escape_next = False
        while i < len(text):
            ch = text[i]
            if escape_next:
                result.append(ch)
                escape_next = False
            elif ch == "\\":
                result.append(ch)
                escape_next = True
            elif ch == '"':
                if not in_string:
                    in_string = True
                    result.append(ch)
                else:
                    # Check if this quote ends the string value
                    rest = text[i + 1 :].lstrip()
                    if rest and rest[0] in (",", "}", "]", ":"):
                        in_string = False
                        result.append(ch)
                    elif not rest:
                        in_string = False
                        result.append(ch)
                    else:
                        # Inner quote — escape it
                        result.append('\\"')
            else:
                result.append(ch)
            i += 1
        return "".join(result)

    try:
        fixed = _fix_inner_quotes(cleaned)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Fallback for common errors like missing commas
    try:
        repaired = re.sub(r'("\s*\{)', r'", \{', cleaned)
        repaired = re.sub(r'(\})(\s*")', r"\1, \2", repaired)
        return json.loads(repaired)
    except Exception:
        print(f"⚠️ JSON parsing failed. Preview: {repr(cleaned[:400])}")
        return {}


def detect_language(text: str) -> str:
    """Detect if text is primarily Chinese or English."""
    # Count Chinese characters (CJK Unified Ideographs)
    chinese_chars = len([c for c in text if "\u4e00" <= c <= "\u9fff"])
    total_chars = len([c for c in text if c.strip()])

    # If more than 30% are Chinese characters, consider it Chinese
    if total_chars > 0 and (chinese_chars / total_chars) > 0.3:
        return "zh"
    return "en"


def _build_qa_prompts(chunk_text: str, difficulty: str, n: int, lang: str) -> tuple[str, str]:
    """Build system and user prompts for QA generation."""
    if lang == "zh":
        difficulty_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
        diff_zh = difficulty_map.get(difficulty, difficulty)

        system_prompt = (
            "你是一个细心的数据集生成器。"
            "生成的问题必须严格基于提供的上下文来回答。"
            "关注核心概念、事实和技术细节。"
            "返回一个包含'items'数组的JSON对象。"
        )

        user_prompt = f"""
上下文：
\"\"\"{chunk_text}\"\"\"

任务：
- 生成 {n} 个{diff_zh}难度的问答对。
- 每个答案必须完全基于上下文支持。
- 提供简短的理由（1-2句话）和引用的支持片段。
- 不要生成关于URL、仓库链接、安装命令或示例输出/示例代码的琐碎问题。
- 关注上下文中的核心概念、事实和技术细节。
- 每个问题应测试对内容的真正理解，而不仅仅是表面细节。
- 输出JSON对象：{{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}。
""".strip()
    else:
        system_prompt = (
            "You are a careful dataset generator. "
            "Generate questions strictly answerable from the provided context. "
            "Focus on substantive concepts, facts, and technical details. "
            "Generate questions and answers in the SAME language as the context. "
            "Return a JSON object with an 'items' array."
        )

        user_prompt = f"""
Context:
\"\"\"{chunk_text}\"\"\"

Task:
- Generate {n} {difficulty} question-answer pairs.
- Each answer must be fully supported by the context.
- Provide a short rationale (1–2 sentences) and a quoted supporting span.
- Do NOT generate trivial questions about URLs, repo links, install commands, or example output/sample code.
- Focus on core concepts, factual claims, and technical details in the context.
- Each question should test genuine understanding of the content, not surface-level details.
- Output a JSON object: {{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}.
""".strip()

    return system_prompt, user_prompt


def generate_qa_for_chunk(
    chunk_text: str, difficulty: str, n: int = 2, provider=None, model: str = None
) -> list[dict[str, Any]]:
    """
    Generates question-answer pairs for a given text chunk using any LLM provider.

    Args:
        chunk_text: Text to generate QA pairs from
        difficulty: Question difficulty ('easy', 'medium', 'hard')
        n: Number of QA pairs to generate
        provider: LLM provider instance (auto-detected if None)
        model: Model name (uses provider default if None)

    Returns:
        List of QA pair dictionaries
    """
    # Get LLM provider
    if provider is None:
        from .providers import get_provider

        provider = get_provider(model=model)

    # Detect language and build prompts
    lang = detect_language(chunk_text)
    system_prompt, user_prompt = _build_qa_prompts(chunk_text, difficulty, n, lang)

    try:
        # Call LLM provider
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = provider.generate(
            messages=messages,
            temperature=0.7,
            json_mode=True,
            max_tokens=4096,
        )

        raw_content = response.content
        data = safe_json_parse(raw_content)
        items = data.get("items", [])
    except Exception as e:
        print(f"⚠️ Model API call failed: {e}")
        items = []

    processed_qas = []
    for item in items:
        if item.get("question") and item.get("answer"):
            processed_qas.append(
                {
                    "id": str(uuid.uuid4()),
                    "question": (item.get("question") or "").strip(),
                    "answer": (item.get("answer") or "").strip(),
                    "rationale": (item.get("rationale") or "").strip(),
                    "support_span": (item.get("support_span") or "").strip(),
                }
            )

    return processed_qas


async def agenerate_qa_for_chunk(
    chunk_text: str, difficulty: str, n: int = 2, provider=None, model: str = None
) -> list[dict[str, Any]]:
    """
    Async version: Generates question-answer pairs for a given text chunk.

    Args:
        chunk_text: Text to generate QA pairs from
        difficulty: Question difficulty ('easy', 'medium', 'hard')
        n: Number of QA pairs to generate
        provider: LLM provider instance (auto-detected if None)
        model: Model name (uses provider default if None)

    Returns:
        List of QA pair dictionaries
    """
    # Get LLM provider
    if provider is None:
        from .providers import get_provider

        provider = get_provider(model=model)

    # Detect language and build prompts
    lang = detect_language(chunk_text)
    system_prompt, user_prompt = _build_qa_prompts(chunk_text, difficulty, n, lang)

    try:
        # Call LLM provider asynchronously
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await provider.agenerate(
            messages=messages,
            temperature=0.7,
            json_mode=True,
            max_tokens=4096,
        )

        raw_content = response.content
        data = safe_json_parse(raw_content)
        items = data.get("items", [])
    except Exception as e:
        print(f"⚠️ Model API call failed: {e}")
        items = []

    processed_qas = []
    for item in items:
        if item.get("question") and item.get("answer"):
            processed_qas.append(
                {
                    "id": str(uuid.uuid4()),
                    "question": (item.get("question") or "").strip(),
                    "answer": (item.get("answer") or "").strip(),
                    "rationale": (item.get("rationale") or "").strip(),
                    "support_span": (item.get("support_span") or "").strip(),
                }
            )

    return processed_qas
