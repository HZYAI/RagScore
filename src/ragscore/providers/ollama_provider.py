"""
Ollama Provider for RAGScore

Supports local LLM inference via Ollama.
https://ollama.ai/
"""

import logging
import os
from typing import Optional

import requests

from ..exceptions import LLMConnectionError, LLMError
from .base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    LLM Provider for Ollama (local LLM inference).

    Ollama runs models locally - no API key required!

    Usage:
        provider = OllamaProvider(model="llama2")
        response = provider.generate("Hello, world!")

    Supported models (examples):
        - llama2, llama2:13b, llama2:70b
        - mistral, mixtral
        - codellama
        - phi
        - neural-chat
        - starling-lm
        - And many more: https://ollama.ai/library
    """

    PROVIDER_NAME = "ollama"
    DEFAULT_MODEL = "llama2"
    DEFAULT_BASE_URL = "http://localhost:11434"

    # Preferred models in order (pick first available)
    _PREFERRED_MODELS = [
        "llama3",
        "llama3.2",
        "llama3.1",
        "llama3:8b",
        "llama3.2:3b",
        "mistral",
        "qwen2.5",
        "qwen2",
        "phi3",
        "gemma2",
        "llama2",
    ]

    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        timeout: int = 300,  # Local models can be slow, especially reasoning models
        **kwargs,
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Model name (e.g., "llama2", "mistral", "codellama")
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", self.DEFAULT_BASE_URL)
        self.base_url = self.base_url.rstrip("/")
        self.timeout = timeout
        self._server_checked = False

        # Resolve model: explicit > env var > auto-detect > fallback
        self.model = model or os.getenv("OLLAMA_MODEL") or self._auto_detect_model()

        logger.info(f"Initialized Ollama provider with model: {self.model}")

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    @property
    def model_name(self) -> str:
        return self.model

    def _check_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _auto_detect_model(self) -> str:
        """Pick the best available model, preferring llama3 variants."""
        try:
            available = self.list_models()
            if not available:
                return self.DEFAULT_MODEL

            # Match preferred models (prefix match to handle tags like llama3:8b)
            for preferred in self._PREFERRED_MODELS:
                for avail in available:
                    if avail == preferred or avail.startswith(preferred + ":"):
                        logger.info(f"Auto-selected Ollama model: {avail}")
                        return avail

            # No preferred match — use first available
            logger.info(f"Using first available Ollama model: {available[0]}")
            return available[0]
        except Exception:
            return self.DEFAULT_MODEL

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        json_mode: bool = False,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (default: 0.7)
            json_mode: Request JSON output format
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated text
        """
        if not self._server_checked:
            if not self._check_server():
                raise LLMConnectionError("Ollama server not running. Start it with: ollama serve")
            self._server_checked = True

        temp = temperature if temperature is not None else 0.7

        try:
            request_json = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "num_predict": max_tokens,
                },
            }

            # Add JSON format hint if requested
            if json_mode:
                request_json["format"] = "json"

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_json,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            message = data.get("message", {})

            return LLMResponse(
                content=message.get("content", ""),
                model=self.model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                raw_response=data,
            )

        except requests.exceptions.Timeout as e:
            raise LLMError(
                f"Ollama request timed out after {self.timeout}s. "
                "Try a smaller model or increase timeout."
            ) from e
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                available = self.list_models()
                models_str = ", ".join(available[:10]) if available else "none found"
                raise LLMError(
                    f"Model '{self.model}' not found in Ollama. "
                    f"Available models: [{models_str}]. "
                    f"Pull it with: ollama pull {self.model}"
                ) from e
            raise LLMConnectionError(f"Ollama HTTP error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise LLMConnectionError(f"Failed to connect to Ollama: {e}") from e

    def get_embeddings(self, texts: list[str], model: Optional[str] = None) -> list[list[float]]:
        """
        Generate embeddings using Ollama.

        Args:
            texts: List of texts to embed
            model: Embedding model (default: same as chat model)

        Returns:
            List of embedding vectors
        """
        if not self._check_server():
            raise LLMConnectionError("Ollama server not running")

        embed_model = model or self.model
        embeddings = []

        for text in texts:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": embed_model, "prompt": text},
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                embeddings.append(data.get("embedding", []))

            except requests.exceptions.RequestException as e:
                raise LLMError(f"Ollama failed to get embeddings: {e}") from e

        return embeddings

    def list_models(self) -> list[str]:
        """List available models in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            data = response.json()
            return [model["name"] for model in data.get("models", [])]

        except requests.exceptions.RequestException:
            return []
