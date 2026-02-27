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
    """Detect text language: Chinese (zh), Japanese (ja), German (de), or English (en)."""
    total_chars = len([c for c in text if c.strip()])
    if total_chars == 0:
        return "en"

    # Count CJK characters (shared by Chinese and Japanese)
    cjk_chars = len([c for c in text if "\u4e00" <= c <= "\u9fff"])

    # Count Japanese-specific characters (Hiragana + Katakana)
    ja_chars = len([c for c in text if "\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff"])

    # Japanese: has Hiragana/Katakana (unique to Japanese)
    if ja_chars > 0 and (ja_chars + cjk_chars) / total_chars > 0.15:
        return "ja"

    # Chinese: CJK characters without Japanese kana
    if cjk_chars / total_chars > 0.3:
        return "zh"

    # German: detect common German words and characters
    lower_text = text.lower()
    german_markers = [
        " der ",
        " die ",
        " das ",
        " und ",
        " ist ",
        " ein ",
        " eine ",
        " mit ",
        " für ",
        " auf ",
        " von ",
        " den ",
        " dem ",
        " wird ",
        " sind ",
        " nicht ",
        "ä",
        "ö",
        "ü",
        "ß",
    ]
    german_score = sum(1 for m in german_markers if m in lower_text)
    if german_score >= 4:
        return "de"

    return "en"


def _build_qa_prompts(
    chunk_text: str,
    difficulty: str,
    n: int,
    lang: str,
    audience: str = None,
    purpose: str = None,
) -> tuple[str, str]:
    """Build system and user prompts for QA generation.

    Args:
        chunk_text: The document chunk to generate QA from.
        difficulty: Question difficulty ('easy', 'medium', 'hard').
        n: Number of QA pairs to generate.
        lang: Language code ('en', 'zh', 'ja', 'de').
        audience: Target audience (e.g. 'internal staff', 'customers', 'developers').
        purpose: Document purpose (e.g. 'training', 'compliance', 'product FAQ').
    """
    if lang == "zh":
        difficulty_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
        diff_zh = difficulty_map.get(difficulty, difficulty)

        # Build audience/purpose instruction for Chinese
        intent_instructions_zh = ""
        if audience or purpose:
            intent_instructions_zh = "\n"
            if audience:
                intent_instructions_zh += (
                    f"- 目标读者：{audience}。生成的问题应该是该读者群体实际会提出的问题。\n"
                )
            if purpose:
                intent_instructions_zh += (
                    f"- 文档用途：{purpose}。生成的问题应围绕该用途的核心关注点。\n"
                )

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
- 每个问题应测试对内容的真正理解，而不仅仅是表面细节。{intent_instructions_zh}
- 输出JSON对象：{{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}。
""".strip()
    elif lang == "ja":
        difficulty_map = {"easy": "簡単", "medium": "中級", "hard": "難問"}
        diff_ja = difficulty_map.get(difficulty, difficulty)

        intent_instructions_ja = ""
        if audience or purpose:
            intent_instructions_ja = "\n"
            if audience:
                intent_instructions_ja += (
                    f"- 対象読者：{audience}。この読者が実際に尋ねる質問を生成してください。\n"
                )
            if purpose:
                intent_instructions_ja += (
                    f"- 文書の目的：{purpose}。この目的に関連する質問を重点的に生成してください。\n"
                )

        system_prompt = (
            "あなたは正確なデータセット生成器です。"
            "質問は提供されたコンテキストに基づいて厳密に回答可能でなければなりません。"
            "核心的な概念、事実、技術的詳細に焦点を当ててください。"
            "'items'配列を含むJSONオブジェクトを返してください。"
        )

        user_prompt = f"""
コンテキスト：
\"\"\"{chunk_text}\"\"\"

タスク：
- {n}個の{diff_ja}レベルの質問と回答のペアを生成してください。
- 各回答はコンテキストによって完全に裏付けられている必要があります。
- 簡潔な根拠（1〜2文）と引用された裏付け部分を提供してください。
- URL、リポジトリリンク、インストールコマンド、サンプル出力に関する些細な質問は生成しないでください。
- コンテキスト内の核心的な概念、事実、技術的詳細に焦点を当ててください。
- 各質問は、表面的な詳細ではなく、内容の真の理解をテストする必要があります。{intent_instructions_ja}
- JSONオブジェクトを出力：{{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}。
""".strip()
    elif lang == "de":
        difficulty_map = {"easy": "einfach", "medium": "mittel", "hard": "schwer"}
        diff_de = difficulty_map.get(difficulty, difficulty)

        intent_instructions_de = ""
        if audience or purpose:
            intent_instructions_de = "\n"
            if audience:
                intent_instructions_de += f"- Zielgruppe: {audience}. Generieren Sie Fragen, die diese Zielgruppe realistisch stellen würde.\n"
            if purpose:
                intent_instructions_de += f"- Dokumentzweck: {purpose}. Konzentrieren Sie die Fragen auf das, was für diesen Zweck wichtig ist.\n"

        system_prompt = (
            "Sie sind ein sorgfältiger Datensatz-Generator. "
            "Generieren Sie Fragen, die ausschließlich aus dem bereitgestellten Kontext beantwortbar sind. "
            "Konzentrieren Sie sich auf wesentliche Konzepte, Fakten und technische Details. "
            "Geben Sie ein JSON-Objekt mit einem 'items'-Array zurück."
        )

        user_prompt = f"""
Kontext:
\"\"\"{chunk_text}\"\"\"

Aufgabe:
- Generieren Sie {n} Frage-Antwort-Paare mit dem Schwierigkeitsgrad {diff_de}.
- Jede Antwort muss vollständig durch den Kontext belegt sein.
- Geben Sie eine kurze Begründung (1–2 Sätze) und ein zitiertes Belegfragment an.
- Generieren Sie KEINE trivialen Fragen zu URLs, Repository-Links, Installationsbefehlen oder Beispielausgaben.
- Konzentrieren Sie sich auf Kernkonzepte, Fakten und technische Details im Kontext.
- Jede Frage sollte echtes Verständnis des Inhalts testen, nicht nur oberflächliche Details.{intent_instructions_de}
- JSON-Objekt ausgeben: {{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}.
""".strip()
    else:
        # Build audience/purpose instruction for English
        intent_instructions_en = ""
        if audience or purpose:
            intent_instructions_en = "\n"
            if audience:
                intent_instructions_en += f"- Target audience: {audience}. Generate questions this audience would realistically ask.\n"
            if purpose:
                intent_instructions_en += f"- Document purpose: {purpose}. Focus questions on what matters for this purpose.\n"

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
- Each question should test genuine understanding of the content, not surface-level details.{intent_instructions_en}
- Output a JSON object: {{"items": [{{"question": "...", "answer": "...", "rationale": "...", "support_span": "..."}}]}}.
""".strip()

    return system_prompt, user_prompt


def generate_qa_for_chunk(
    chunk_text: str,
    difficulty: str,
    n: int = 2,
    provider=None,
    model: str = None,
    audience: str = None,
    purpose: str = None,
) -> list[dict[str, Any]]:
    """
    Generates question-answer pairs for a given text chunk using any LLM provider.

    Args:
        chunk_text: Text to generate QA pairs from
        difficulty: Question difficulty ('easy', 'medium', 'hard')
        n: Number of QA pairs to generate
        provider: LLM provider instance (auto-detected if None)
        model: Model name (uses provider default if None)
        audience: Target audience (e.g. 'developers', 'customers')
        purpose: Document purpose (e.g. 'training', 'faq', 'compliance')

    Returns:
        List of QA pair dictionaries
    """
    # Get LLM provider
    if provider is None:
        from .providers import get_provider

        provider = get_provider(model=model)

    # Detect language and build prompts
    lang = detect_language(chunk_text)
    system_prompt, user_prompt = _build_qa_prompts(
        chunk_text, difficulty, n, lang, audience=audience, purpose=purpose
    )

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
    chunk_text: str,
    difficulty: str,
    n: int = 2,
    provider=None,
    model: str = None,
    audience: str = None,
    purpose: str = None,
) -> list[dict[str, Any]]:
    """
    Async version: Generates question-answer pairs for a given text chunk.

    Args:
        chunk_text: Text to generate QA pairs from
        difficulty: Question difficulty ('easy', 'medium', 'hard')
        n: Number of QA pairs to generate
        provider: LLM provider instance (auto-detected if None)
        model: Model name (uses provider default if None)
        audience: Target audience (e.g. 'developers', 'customers')
        purpose: Document purpose (e.g. 'training', 'faq', 'compliance')

    Returns:
        List of QA pair dictionaries
    """
    # Get LLM provider
    if provider is None:
        from .providers import get_provider

        provider = get_provider(model=model)

    # Detect language and build prompts
    lang = detect_language(chunk_text)
    system_prompt, user_prompt = _build_qa_prompts(
        chunk_text, difficulty, n, lang, audience=audience, purpose=purpose
    )

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
