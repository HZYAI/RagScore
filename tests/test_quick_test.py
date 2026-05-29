"""Tests for quick_test failure handling."""

import importlib

import pytest

from ragscore.exceptions import RAGScoreError


@pytest.mark.asyncio
async def test_quick_test_raises_when_all_generated_chunks_fail(monkeypatch, tmp_path):
    """Provider failures should surface instead of returning an unusable empty result."""
    quick_test_module = importlib.import_module("ragscore.quick_test")
    doc_path = tmp_path / "doc.txt"
    doc_path.write_text(" ".join(f"word{i}" for i in range(100)), encoding="utf-8")

    async def fail_generation(*args, **kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(quick_test_module, "agenerate_qa_for_chunk", fail_generation)

    with pytest.raises(RAGScoreError, match="No test results generated"):
        await quick_test_module._quick_test_async(
            endpoint=lambda question: "answer",
            docs=doc_path,
            n=1,
            provider=object(),
            judge_provider=object(),
            silent=True,
        )
