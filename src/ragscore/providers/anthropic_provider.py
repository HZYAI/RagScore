"""
Anthropic Provider for RAGScore

Supports Claude models via Anthropic API.
"""

import logging
import os
from typing import Optional

from ..exceptions import LLMError, LLMRateLimitError, MissingAPIKeyError
from .base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    LLM Provider for Anthropic Claude models.

    Usage:
        provider = AnthropicProvider(model="claude-3-sonnet-20240229")
        response = provider.generate("Hello!")

    Models:
        - claude-3-opus-20240229 (most capable)
        - claude-3-sonnet-20240229 (balanced)
        - claude-3-haiku-20240307 (fastest)
        - claude-2.1
    """

    PROVIDER_NAME = "anthropic"
    DEFAULT_MODEL = "claude-3-haiku-20240307"

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model name
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise MissingAPIKeyError(
                "ANTHROPIC_API_KEY", "Get your API key from https://console.anthropic.com/"
            )

        self.model = model or os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)

        # Import anthropic library
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError as e:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            ) from e

        logger.info(f"Initialized Anthropic provider with model: {self.model}")

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

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
        """Generate text using Claude."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )

            # Extract text content from response
            content = ""
            for block in message.content:
                if hasattr(block, "text"):
                    content = block.text
                    break

            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": message.usage.input_tokens,
                    "completion_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens,
                },
                raw_response=message.model_dump(),
            )

        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "limit" in error_str:
                raise LLMRateLimitError(self.PROVIDER_NAME) from e
            raise LLMError(f"Anthropic API error: {e}") from e

    def get_embeddings(self, texts: list[str], model: Optional[str] = None) -> list[list[float]]:
        """
        Anthropic doesn't provide embeddings API.
        Use OpenAI or another provider for embeddings.
        """
        raise NotImplementedError(
            "Anthropic doesn't provide embeddings. Use OpenAI or another provider for embeddings."
        )
