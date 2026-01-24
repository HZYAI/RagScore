"""
Base LLM Provider Interface

Defines the abstract interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    content: str
    raw_response: dict[str, Any]
    model: str
    usage: Optional[dict[str, int]] = None  # tokens used

    @property
    def is_json(self) -> bool:
        """Check if content appears to be JSON."""
        content = self.content.strip()
        return content.startswith("{") or content.startswith("[")


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement:
    - generate(): Text generation
    - embed(): Text embedding (optional)
    """

    provider_name: str = "base"
    supports_json_mode: bool = False
    supports_embeddings: bool = False

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, **kwargs):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional provider-specific options
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.options = kwargs

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            json_mode: Request JSON output format
            **kwargs: Additional generation options

        Returns:
            LLMResponse with generated content
        """
        pass

    async def agenerate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """
        Async generate text from the LLM.

        Default implementation runs synchronous generate() in a thread pool.
        Providers can override this with native async implementations.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            json_mode: Request JSON output format
            **kwargs: Additional generation options

        Returns:
            LLMResponse with generated content
        """
        import asyncio
        from functools import partial

        loop = asyncio.get_running_loop()
        func = partial(
            self.generate,
            messages=messages,
            temperature=temperature,
            json_mode=json_mode,
            **kwargs,
        )
        return await loop.run_in_executor(None, func)

    def embed(self, texts: list[str], **kwargs) -> list[list[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of texts to embed
            **kwargs: Additional embedding options

        Returns:
            List of embedding vectors

        Raises:
            NotImplementedError: If provider doesn't support embeddings
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support embeddings. Use a dedicated embedding provider."
        )

    def _validate_messages(self, messages: list[dict[str, str]]) -> None:
        """Validate message format."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise ValueError(f"Message {i} must be a dict, got {type(msg)}")
            if "role" not in msg:
                raise ValueError(f"Message {i} missing 'role' field")
            if "content" not in msg:
                raise ValueError(f"Message {i} missing 'content' field")
            if msg["role"] not in ("system", "user", "assistant"):
                raise ValueError(f"Invalid role '{msg['role']}' in message {i}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
