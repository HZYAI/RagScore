"""
LLM Provider Factory

Factory functions to create and manage LLM provider instances.
Supports: OpenAI, DashScope, Anthropic, Ollama, Grok, Groq, Together, and more.
"""

import logging
import os
from typing import Any, Optional

from ..exceptions import InvalidProviderError, MissingAPIKeyError
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

# Registry of available providers
_PROVIDER_REGISTRY: dict[str, type[BaseLLMProvider]] = {}

# Pre-configured providers with their environment variable keys
PROVIDER_ENV_KEYS = {
    "dashscope": "DASHSCOPE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "grok": "XAI_API_KEY",
    "together": "TOGETHER_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": None,  # No API key needed
    "custom": "LLM_API_KEY",
}


def register_provider(name: str, provider: type[BaseLLMProvider]):
    """Register a provider."""
    _PROVIDER_REGISTRY[name] = provider


def _register_default_providers():
    """Register all available providers."""
    # DashScope provider
    try:
        from .dashscope_provider import DashScopeProvider

        register_provider("dashscope", DashScopeProvider)
        register_provider("qwen", DashScopeProvider)  # Alias
    except ImportError:
        logger.debug("DashScope provider not available")

    # OpenAI provider
    try:
        from .openai_provider import AzureOpenAIProvider, OpenAIProvider

        register_provider("openai", OpenAIProvider)
        register_provider("azure", AzureOpenAIProvider)
        register_provider("azure_openai", AzureOpenAIProvider)  # Alias
    except ImportError:
        logger.debug("OpenAI provider not available")

    # Anthropic provider
    try:
        from .anthropic_provider import AnthropicProvider

        register_provider("anthropic", AnthropicProvider)
        register_provider("claude", AnthropicProvider)  # Alias
    except ImportError:
        logger.debug("Anthropic provider not available")

    # Ollama provider (local LLM)
    try:
        from .ollama_provider import OllamaProvider

        register_provider("ollama", OllamaProvider)
        register_provider("local", OllamaProvider)  # Alias
    except ImportError:
        logger.debug("Ollama provider not available")

    # Generic OpenAI-compatible providers
    try:
        from .generic_provider import (
            DeepSeekProvider,
            GenericOpenAIProvider,
            GrokProvider,
            GroqProvider,
            MistralProvider,
            TogetherProvider,
        )

        register_provider("generic", GenericOpenAIProvider)
        register_provider("custom", GenericOpenAIProvider)
        register_provider("grok", GrokProvider)
        register_provider("xai", GrokProvider)  # Alias
        register_provider("together", TogetherProvider)
        register_provider("groq", GroqProvider)
        register_provider("mistral", MistralProvider)
        register_provider("deepseek", DeepSeekProvider)
    except ImportError:
        logger.debug("Generic providers not available")


_register_default_providers()


def list_providers() -> list[str]:
    """
    List available provider names.

    Returns:
        List of provider names that can be used with get_provider()
    """
    return list(_PROVIDER_REGISTRY.keys())


def get_provider(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> BaseLLMProvider:
    """
    Get an LLM provider instance.

    Args:
        provider: Provider name ('dashscope', 'openai', 'azure')
                 If not specified, auto-detects based on available API keys
        api_key: API key (optional, can use environment variables)
        model: Model name (optional, uses provider default)
        **kwargs: Additional provider-specific options

    Returns:
        Configured LLM provider instance

    Raises:
        InvalidProviderError: If provider name is not recognized
        MissingAPIKeyError: If no API key is available

    Example:
        >>> provider = get_provider("openai", model="gpt-4o")
        >>> response = provider.generate([{"role": "user", "content": "Hello"}])
    """
    # Auto-detect provider if not specified
    if provider is None:
        provider = auto_detect_provider()
        if provider is None:
            raise MissingAPIKeyError(
                "No provider specified and no API keys found",
                "Set an API key environment variable or specify a provider",
            )

    provider = provider.lower()

    if provider not in _PROVIDER_REGISTRY:
        raise InvalidProviderError(provider, list(_PROVIDER_REGISTRY.keys()))

    provider_class = _PROVIDER_REGISTRY[provider]

    # Build kwargs
    init_kwargs: dict[str, Any] = {}
    if api_key:
        init_kwargs["api_key"] = api_key
    if model:
        init_kwargs["model"] = model
    init_kwargs.update(kwargs)

    return provider_class(**init_kwargs)


def auto_detect_provider() -> Optional[str]:
    """
    Auto-detect available provider based on environment variables.

    Checks for API keys in order of preference.

    Returns:
        Provider name if found, None otherwise
    """
    # Order of preference (most common first)
    checks = [
        ("openai", "OPENAI_API_KEY"),
        ("dashscope", "DASHSCOPE_API_KEY"),
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("grok", "XAI_API_KEY"),
        ("groq", "GROQ_API_KEY"),
        ("together", "TOGETHER_API_KEY"),
        ("mistral", "MISTRAL_API_KEY"),
        ("deepseek", "DEEPSEEK_API_KEY"),
        ("azure", "AZURE_OPENAI_API_KEY"),
        ("fireworks", "FIREWORKS_API_KEY"),
        ("perplexity", "PERPLEXITY_API_KEY"),
        ("openrouter", "OPENROUTER_API_KEY"),
    ]

    for provider_name, env_var in checks:
        if os.getenv(env_var):
            logger.info(f"Auto-detected provider: {provider_name}")
            return provider_name

    # Check if Ollama is running locally
    try:
        import requests  # type: ignore[import-untyped]

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            logger.info("Auto-detected provider: ollama (local)")
            return "ollama"
    except Exception:
        pass

    # Check for custom endpoint
    if os.getenv("LLM_BASE_URL"):
        logger.info("Auto-detected provider: custom")
        return "custom"

    return None


def get_default_provider_config() -> dict[str, Any]:
    """
    Get configuration for the default provider.

    Returns:
        Dict with provider name and default model
    """
    try:
        provider = auto_detect_provider()
        if provider is None:
            return {
                "provider": None,
                "model": None,
                "embedding_model": None,
            }
        provider_class = _PROVIDER_REGISTRY[provider]
        return {
            "provider": provider,
            "model": getattr(provider_class, "DEFAULT_MODEL", None),
            "embedding_model": getattr(provider_class, "EMBEDDING_MODEL", None),
        }
    except (MissingAPIKeyError, KeyError):
        return {
            "provider": None,
            "model": None,
            "embedding_model": None,
        }
