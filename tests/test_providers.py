"""Tests for the LLM providers module."""

from unittest.mock import MagicMock, patch

import pytest

from ragscore.exceptions import (
    InvalidProviderError,
    LLMRateLimitError,
    MissingAPIKeyError,
)
from ragscore.providers.base import BaseLLMProvider, LLMResponse
from ragscore.providers.factory import auto_detect_provider, get_provider, list_providers


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_basic_response(self):
        """Test creating a basic response."""
        resp = LLMResponse(
            content="Hello, world!", raw_response={"output": "test"}, model="test-model"
        )

        assert resp.content == "Hello, world!"
        assert resp.model == "test-model"
        assert resp.usage is None

    def test_response_with_usage(self):
        """Test response with token usage."""
        resp = LLMResponse(
            content="Test",
            raw_response={},
            model="test",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

        assert resp.usage["total_tokens"] == 30

    def test_is_json_detection(self):
        """Test JSON content detection."""
        json_resp = LLMResponse(content='{"key": "value"}', raw_response={}, model="test")
        assert json_resp.is_json is True

        text_resp = LLMResponse(content="Just plain text", raw_response={}, model="test")
        assert text_resp.is_json is False


class TestBaseLLMProvider:
    """Test BaseLLMProvider abstract class."""

    def test_cannot_instantiate_directly(self):
        """Test that abstract class cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseLLMProvider()


class TestProviderFactory:
    """Test provider factory functions."""

    def test_list_providers(self):
        """Test listing available providers."""
        providers = list_providers()

        assert isinstance(providers, list)
        assert "dashscope" in providers
        # OpenAI may or may not be available depending on install

    def test_get_provider_invalid(self, mock_api_keys):
        """Test getting invalid provider raises error."""
        with pytest.raises(InvalidProviderError):
            get_provider("nonexistent_provider")

    def test_auto_detect_dashscope(self, monkeypatch):
        """Test auto-detection selects DashScope when key is set."""
        monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        provider = auto_detect_provider()
        assert provider == "dashscope"

    def test_auto_detect_openai(self, monkeypatch):
        """Test auto-detection selects OpenAI when only that key is set."""
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        provider = auto_detect_provider()
        assert provider == "openai"

    def test_auto_detect_no_keys(self, monkeypatch):
        """Test auto-detection returns None when no keys are set."""
        # Clear all API keys
        for key in [
            "OPENAI_API_KEY",
            "DASHSCOPE_API_KEY",
            "ANTHROPIC_API_KEY",
            "XAI_API_KEY",
            "GROQ_API_KEY",
            "TOGETHER_API_KEY",
            "MISTRAL_API_KEY",
            "DEEPSEEK_API_KEY",
            "AZURE_OPENAI_API_KEY",
            "LLM_BASE_URL",
        ]:
            monkeypatch.delenv(key, raising=False)

        provider = auto_detect_provider()
        # May return "ollama" if Ollama is running locally, otherwise None
        assert provider is None or provider == "ollama"


class TestDashScopeProvider:
    """Test DashScope provider."""

    def test_missing_api_key(self, monkeypatch):
        """Test error when API key is missing."""
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

        from ragscore.providers.dashscope_provider import DashScopeProvider

        with pytest.raises(MissingAPIKeyError):
            DashScopeProvider()

    def test_provider_name(self, mock_api_keys):
        """Test provider name is set correctly."""
        with patch("dashscope.Generation"):
            from ragscore.providers.dashscope_provider import DashScopeProvider

            provider = DashScopeProvider()
            assert provider.provider_name == "dashscope"

    def test_default_model(self, mock_api_keys):
        """Test default model is set."""
        with patch("dashscope.Generation"):
            from ragscore.providers.dashscope_provider import DashScopeProvider

            provider = DashScopeProvider()
            assert provider.model == "qwen-turbo"

    def test_generate_success(self, mock_api_keys):
        """Test successful generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {"choices": [{"message": {"content": "Test response"}}]}

        with patch("dashscope.Generation") as mock_gen:
            mock_gen.call.return_value = mock_response

            from ragscore.providers.dashscope_provider import DashScopeProvider

            provider = DashScopeProvider()
            response = provider.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Test response"
            assert response.model == "qwen-turbo"

    def test_generate_rate_limit(self, mock_api_keys):
        """Test rate limit error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.message = "Rate limit exceeded"

        with patch("dashscope.Generation") as mock_gen:
            mock_gen.call.return_value = mock_response

            from ragscore.providers.dashscope_provider import DashScopeProvider

            provider = DashScopeProvider()

            with pytest.raises(LLMRateLimitError):
                provider.generate([{"role": "user", "content": "Hello"}])


class TestOpenAIProvider:
    """Test OpenAI provider."""

    def test_missing_api_key(self, monkeypatch):
        """Test error when API key is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        from ragscore.providers.openai_provider import OpenAIProvider

        with pytest.raises(MissingAPIKeyError):
            OpenAIProvider()

    def test_provider_name(self, mock_openai_client):
        """Test provider name is set correctly."""
        from ragscore.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider()
        assert provider.provider_name == "openai"

    def test_default_model(self, mock_openai_client):
        """Test default model is set."""
        from ragscore.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider()
        assert provider.model == "gpt-4o-mini"

    def test_custom_base_url(self, mock_openai_client):
        """Test custom base URL for OpenAI-compatible APIs."""
        from ragscore.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(base_url="http://localhost:8080/v1")
        assert provider.base_url == "http://localhost:8080/v1"

    def test_generate_success(self, mock_openai_client):
        """Test successful generation."""
        from ragscore.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider()
        response = provider.generate([{"role": "user", "content": "Hello"}])

        assert response is not None
        assert response.model == "gpt-4o-mini"


class TestProviderIntegration:
    """Integration tests for providers."""

    def test_get_dashscope_provider(self, mock_api_keys):
        """Test getting DashScope provider through factory."""
        with patch("dashscope.Generation"):
            provider = get_provider("dashscope")
            assert provider.provider_name == "dashscope"

    def test_get_openai_provider(self, mock_openai_client):
        """Test getting OpenAI provider through factory."""
        provider = get_provider("openai")
        assert provider.provider_name == "openai"

    def test_get_provider_with_custom_model(self, mock_api_keys):
        """Test getting provider with custom model."""
        with patch("dashscope.Generation"):
            provider = get_provider("dashscope", model="qwen-plus")
            assert provider.model == "qwen-plus"
