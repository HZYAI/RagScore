"""
OpenAI LLM Provider

Supports GPT models via the OpenAI API.
Also works with OpenAI-compatible APIs (Azure, local servers, etc.)
"""

from typing import Optional

from ..exceptions import LLMConnectionError, LLMRateLimitError, MissingAPIKeyError
from .base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider for GPT models.

    Supported models:
    - gpt-4o (latest, recommended)
    - gpt-4o-mini (fast, cost-effective)
    - gpt-4-turbo (high quality)
    - gpt-3.5-turbo (legacy, fast)

    Also supports OpenAI-compatible APIs via base_url parameter.
    """

    provider_name = "openai"
    supports_json_mode = True
    supports_embeddings = True

    DEFAULT_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        base_url: str = None,
        embedding_model: str = None,
        **kwargs,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini)
            temperature: Sampling temperature
            base_url: Optional custom API URL for OpenAI-compatible services
            embedding_model: Model for embeddings (default: text-embedding-3-small)
        """
        import os

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise MissingAPIKeyError("OpenAI", "OPENAI_API_KEY")

        model = model or self.DEFAULT_MODEL
        super().__init__(api_key, model, temperature, **kwargs)

        self.base_url = base_url
        self.embedding_model = embedding_model or self.EMBEDDING_MODEL

        # Import and configure openai
        try:
            from openai import OpenAI

            client_kwargs = {"api_key": self.api_key}
            if base_url:
                client_kwargs["base_url"] = base_url

            self._client = OpenAI(**client_kwargs)
        except ImportError as e:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            ) from e

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> LLMResponse:
        """Generate text using OpenAI."""
        self._validate_messages(messages)

        temp = temperature if temperature is not None else self.temperature

        call_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
        }

        if json_mode:
            call_kwargs["response_format"] = {"type": "json_object"}

        call_kwargs.update(kwargs)

        try:
            response = self._client.chat.completions.create(**call_kwargs)

            content = response.choices[0].message.content

            # Extract usage
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return LLMResponse(
                content=content,
                raw_response=response.model_dump(),
                model=response.model,
                usage=usage,
            )

        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                raise LLMRateLimitError("OpenAI") from e
            raise LLMConnectionError(f"OpenAI API call failed: {str(e)}") from e

    def embed(self, texts: list[str], **kwargs) -> list[list[float]]:
        """Generate embeddings using OpenAI."""
        try:
            # Process in batches (OpenAI recommends batching)
            batch_size = kwargs.get("batch_size", 100)
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]

                response = self._client.embeddings.create(model=self.embedding_model, input=batch)

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            return all_embeddings

        except Exception as e:
            raise LLMConnectionError(f"OpenAI embedding failed: {str(e)}") from e


class AzureOpenAIProvider(OpenAIProvider):
    """
    Azure OpenAI provider.

    Uses Azure's hosted OpenAI models.
    """

    provider_name = "azure"

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        azure_endpoint: str = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: str = None,
        **kwargs,
    ):
        """
        Initialize Azure OpenAI provider.

        Args:
            api_key: Azure OpenAI API key (or set AZURE_OPENAI_API_KEY env var)
            model: Model/deployment name
            temperature: Sampling temperature
            azure_endpoint: Azure endpoint URL (or set AZURE_OPENAI_ENDPOINT env var)
            api_version: API version to use
            deployment_name: Deployment name (defaults to model)
        """
        import os

        api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise MissingAPIKeyError("Azure OpenAI", "AZURE_OPENAI_API_KEY")

        azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            raise MissingAPIKeyError("Azure OpenAI", "AZURE_OPENAI_ENDPOINT")

        # Don't call parent __init__ since we need different client setup
        self.api_key = api_key
        self.model = model or deployment_name or "gpt-4o-mini"
        self.temperature = temperature
        self.deployment_name = deployment_name or self.model
        self.options = kwargs

        try:
            from openai import AzureOpenAI

            self._client = AzureOpenAI(
                api_key=self.api_key, azure_endpoint=azure_endpoint, api_version=api_version
            )
        except ImportError as e:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            ) from e
