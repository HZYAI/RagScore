"""Tests for MCP server helpers."""

import importlib
from types import SimpleNamespace

import pytest

from ragscore import config, mcp_server


class DummyMCP:
    def __init__(self, name):
        self.name = name
        self.tools = {}
        self.resources = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator

    def resource(self, uri):
        def decorator(fn):
            self.resources[uri] = fn
            return fn

        return decorator


@pytest.mark.asyncio
async def test_quick_test_rag_honors_explicit_provider(monkeypatch):
    """Explicit MCP provider should not be overridden by Anthropic auto-preference."""
    monkeypatch.setattr(mcp_server, "MCP_AVAILABLE", True)
    monkeypatch.setattr(mcp_server, "FastMCP", DummyMCP)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr(config, "track_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        mcp_server,
        "_detect_provider_info",
        lambda provider=None, model=None: f"provider={provider}, model={model}",
    )

    captured = {}

    class FakeProvider:
        provider_name = "openai"
        model = "test-model"

    def fake_get_provider(provider=None, model=None):
        captured["provider"] = provider
        captured["model"] = model
        return FakeProvider()

    providers_module = importlib.import_module("ragscore.providers")
    quick_test_module = importlib.import_module("ragscore.quick_test")

    monkeypatch.setattr(providers_module, "get_provider", fake_get_provider)

    async def fake_quick_test_async(**kwargs):
        captured["quick_provider"] = kwargs["provider"].provider_name
        return SimpleNamespace(
            passed=True,
            correct=1,
            total=1,
            accuracy=1.0,
            avg_score=5.0,
            corrections=[],
            details=[],
        )

    monkeypatch.setattr(quick_test_module, "_quick_test_async", fake_quick_test_async)

    server = mcp_server.create_mcp_server()
    output = await server.tools["quick_test_rag"](
        endpoint="http://example.test/query",
        docs_path="docs",
        provider="openai",
    )

    assert captured["provider"] == "openai"
    assert captured["quick_provider"] == "openai"
    assert "PASSED" in output
