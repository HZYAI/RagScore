"""
DashScope (Alibaba Cloud) LLM Provider

Supports Qwen models via the DashScope API.
"""

from typing import Optional

from ..exceptions import LLMConnectionError, LLMRateLimitError, MissingAPIKeyError
from .base import BaseLLMProvider, LLMResponse


class DashScopeProvider(BaseLLMProvider):
    """
    DashScope LLM provider for Alibaba Cloud's Qwen models.

    Supported models:
    - qwen-turbo (fast, cost-effective)
    - qwen-plus (balanced)
    - qwen-max (highest quality)
    """

    provider_name = "dashscope"
    supports_json_mode = True
    supports_embeddings = True

    DEFAULT_MODEL = "qwen-turbo"
    EMBEDDING_MODEL = "text-embedding-v3"

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        embedding_model: str = None,
        **kwargs,
    ):
        """
        Initialize DashScope provider.

        Args:
            api_key: DashScope API key (or set DASHSCOPE_API_KEY env var)
            model: Model name (default: qwen-turbo)
            temperature: Sampling temperature
            embedding_model: Model for embeddings (default: text-embedding-v3)
        """
        import os

        api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise MissingAPIKeyError("DashScope", "DASHSCOPE_API_KEY")

        model = model or self.DEFAULT_MODEL
        super().__init__(api_key, model, temperature, **kwargs)

        self.embedding_model = embedding_model or self.EMBEDDING_MODEL

        # Import and configure dashscope
        try:
            import dashscope
            from dashscope import Generation

            dashscope.api_key = self.api_key
            self._generation = Generation
        except ImportError as e:
            raise ImportError(
                "dashscope package not installed. Install with: pip install dashscope"
            ) from e

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """Generate text using DashScope."""
        self._validate_messages(messages)

        temp = temperature if temperature is not None else self.temperature

        call_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
        }

        if json_mode:
            call_kwargs["result_format"] = "json_object"

        call_kwargs.update(kwargs)

        try:
            response = self._generation.call(**call_kwargs)

            # Check for errors
            if response.status_code != 200:
                if response.status_code == 429:
                    raise LLMRateLimitError("DashScope")
                raise LLMConnectionError(
                    f"DashScope API error: {response.status_code} - {response.message}"
                )

            content = response.output["choices"][0]["message"]["content"]

            # Extract usage if available
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": response.usage.get("input_tokens", 0),
                    "completion_tokens": response.usage.get("output_tokens", 0),
                    "total_tokens": response.usage.get("total_tokens", 0),
                }

            return LLMResponse(
                content=content, raw_response=response.output, model=self.model, usage=usage
            )

        except Exception as e:
            if "rate limit" in str(e).lower():
                raise LLMRateLimitError("DashScope") from e
            raise LLMConnectionError(f"DashScope API call failed: {str(e)}") from e

    def embed(self, texts: list[str], **kwargs) -> list[list[float]]:
        """Generate embeddings using DashScope."""
        try:
            from langchain_community.embeddings.dashscope import DashScopeEmbeddings

            embedder = DashScopeEmbeddings(
                model=self.embedding_model, dashscope_api_key=self.api_key
            )

            # Process in batches (DashScope limit is 10)
            batch_size = kwargs.get("batch_size", 10)
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = embedder.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)

            return all_embeddings

        except Exception as e:
            raise LLMConnectionError(f"DashScope embedding failed: {str(e)}") from e
