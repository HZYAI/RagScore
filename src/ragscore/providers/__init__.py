"""
LLM Provider implementations for RAGScore.

Supports multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- DashScope (Qwen models)
- Anthropic (Claude)
- Ollama (Local LLMs)
- Grok (xAI)
- Groq (Fast inference)
- Together AI
- Mistral AI
- DeepSeek
- Any OpenAI-compatible endpoint
"""

from typing import TYPE_CHECKING

from .base import BaseLLMProvider, LLMResponse
from .factory import auto_detect_provider, get_provider, list_providers

# Import providers with graceful fallback
if TYPE_CHECKING:
    from .anthropic_provider import AnthropicProvider
    from .dashscope_provider import DashScopeProvider
    from .generic_provider import (
        DeepSeekProvider,
        GenericOpenAIProvider,
        GrokProvider,
        GroqProvider,
        MistralProvider,
        TogetherProvider,
    )
    from .ollama_provider import OllamaProvider
    from .openai_provider import AzureOpenAIProvider, OpenAIProvider
else:
    # Runtime imports with fallback
    try:
        from .dashscope_provider import DashScopeProvider
    except ImportError:
        DashScopeProvider = None  # type: ignore

    try:
        from .openai_provider import AzureOpenAIProvider, OpenAIProvider
    except ImportError:
        OpenAIProvider = None  # type: ignore
        AzureOpenAIProvider = None  # type: ignore

    try:
        from .anthropic_provider import AnthropicProvider
    except ImportError:
        AnthropicProvider = None  # type: ignore

    try:
        from .ollama_provider import OllamaProvider
    except ImportError:
        OllamaProvider = None  # type: ignore

    try:
        from .generic_provider import (
            DeepSeekProvider,
            GenericOpenAIProvider,
            GrokProvider,
            GroqProvider,
            MistralProvider,
            TogetherProvider,
        )
    except ImportError:
        GenericOpenAIProvider = None  # type: ignore
        GrokProvider = None  # type: ignore
        TogetherProvider = None  # type: ignore
        GroqProvider = None  # type: ignore
        MistralProvider = None  # type: ignore
        DeepSeekProvider = None  # type: ignore

__all__ = [
    # Base
    "BaseLLMProvider",
    "LLMResponse",
    # Factory
    "get_provider",
    "list_providers",
    "auto_detect_provider",
    # Providers
    "DashScopeProvider",
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "GenericOpenAIProvider",
    "GrokProvider",
    "TogetherProvider",
    "GroqProvider",
    "MistralProvider",
    "DeepSeekProvider",
]
