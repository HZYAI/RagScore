"""
Generic OpenAI-Compatible Provider for RAGScore

Supports any OpenAI-compatible API endpoint including:
- Grok (xAI)
- Together AI
- Anyscale
- Groq
- Fireworks AI
- Perplexity
- Mistral AI
- OpenRouter
- Local servers (vLLM, text-generation-webui, LocalAI)
- Any custom endpoint
"""

import logging
import os
from typing import Optional

from ..exceptions import LLMConnectionError, LLMError, LLMRateLimitError, MissingAPIKeyError
from .base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


# Pre-configured endpoints for popular providers
PROVIDER_CONFIGS = {
    "grok": {
        "base_url": "https://api.x.ai/v1",
        "env_key": "XAI_API_KEY",
        "default_model": "grok-beta",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "env_key": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Llama-3-70b-chat-hf",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "default_model": "llama-3.1-70b-versatile",
    },
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "env_key": "FIREWORKS_API_KEY",
        "default_model": "accounts/fireworks/models/llama-v3p1-70b-instruct",
    },
    "perplexity": {
        "base_url": "https://api.perplexity.ai",
        "env_key": "PERPLEXITY_API_KEY",
        "default_model": "llama-3.1-sonar-large-128k-online",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "env_key": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "default_model": "meta-llama/llama-3.1-70b-instruct",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
    },
}


class GenericOpenAIProvider(BaseLLMProvider):
    """
    Generic provider for any OpenAI-compatible API.

    Usage:
        # Use pre-configured provider
        provider = GenericOpenAIProvider(provider_name="grok")

        # Or fully custom endpoint
        provider = GenericOpenAIProvider(
            base_url="https://my-server.com/v1",
            api_key="my-key",
            model="my-model"
        )
    """

    PROVIDER_NAME = "generic"

    def __init__(
        self,
        provider_name: str = None,
        base_url: str = None,
        api_key: str = None,
        model: str = None,
        **kwargs,
    ):
        """
        Initialize generic OpenAI-compatible provider.

        Args:
            provider_name: Pre-configured provider (grok, together, groq, etc.)
            base_url: Custom API base URL
            api_key: API key (or use environment variable)
            model: Model name
        """
        # Use pre-configured settings if provider_name given
        if provider_name and provider_name.lower() in PROVIDER_CONFIGS:
            config = PROVIDER_CONFIGS[provider_name.lower()]
            self.base_url = base_url or config["base_url"]
            self.api_key = api_key or os.getenv(config["env_key"])
            self.model = model or config["default_model"]
            self._provider_name = provider_name.lower()

            if not self.api_key:
                raise MissingAPIKeyError(
                    config["env_key"], f"Set {config['env_key']} environment variable"
                )
        else:
            # Fully custom configuration
            self.base_url = base_url or os.getenv("LLM_BASE_URL")
            self.api_key = api_key or os.getenv("LLM_API_KEY", "")
            self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
            self._provider_name = provider_name or "custom"

            if not self.base_url:
                raise ValueError(
                    "base_url required for custom provider. "
                    "Set LLM_BASE_URL environment variable or pass base_url parameter."
                )

        # Initialize OpenAI client with custom base URL
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key or "not-needed",  # Some local servers don't need keys
                base_url=self.base_url,
            )
        except ImportError as e:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            ) from e

        logger.info(
            f"Initialized {self._provider_name} provider: "
            f"model={self.model}, base_url={self.base_url}"
        )

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self.model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Generate text using the configured API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            choice = response.choices[0]
            usage = response.usage

            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                },
                raw_response=response.model_dump(),
            )

        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "limit" in error_str:
                raise LLMRateLimitError(self._provider_name) from e
            if "connect" in error_str or "timeout" in error_str:
                raise LLMConnectionError(f"{self._provider_name}: {e}") from e
            raise LLMError(f"{self._provider_name} API error: {e}") from e

    def get_embeddings(self, texts: list[str], model: Optional[str] = None) -> list[list[float]]:
        """
        Generate embeddings if the API supports it.

        Note: Not all providers support embeddings.
        """
        embed_model = model or self.model

        try:
            embeddings = []
            for text in texts:
                response = self.client.embeddings.create(model=embed_model, input=text)
                embeddings.append(response.data[0].embedding)
            return embeddings

        except Exception as e:
            raise LLMError(
                f"Embeddings not supported or failed ({self._provider_name}): {e}"
            ) from e

    @classmethod
    def list_supported_providers(cls) -> list[str]:
        """List pre-configured provider names."""
        return list(PROVIDER_CONFIGS.keys())


# Convenience aliases for popular providers
class GrokProvider(GenericOpenAIProvider):
    """xAI Grok provider."""

    def __init__(self, **kwargs):
        super().__init__(provider_name="grok", **kwargs)


class TogetherProvider(GenericOpenAIProvider):
    """Together AI provider."""

    def __init__(self, **kwargs):
        super().__init__(provider_name="together", **kwargs)


class GroqProvider(GenericOpenAIProvider):
    """Groq provider (fast inference)."""

    def __init__(self, **kwargs):
        super().__init__(provider_name="groq", **kwargs)


class MistralProvider(GenericOpenAIProvider):
    """Mistral AI provider."""

    def __init__(self, **kwargs):
        super().__init__(provider_name="mistral", **kwargs)


class DeepSeekProvider(GenericOpenAIProvider):
    """DeepSeek provider."""

    def __init__(self, **kwargs):
        super().__init__(provider_name="deepseek", **kwargs)
