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

from .base import BaseLLMProvider, LLMResponse
from .factory import get_provider, list_providers, auto_detect_provider

# Import providers with graceful fallback
try:
    from .dashscope_provider import DashScopeProvider
except ImportError:
    DashScopeProvider = None

try:
    from .openai_provider import OpenAIProvider, AzureOpenAIProvider
except ImportError:
    OpenAIProvider = None
    AzureOpenAIProvider = None

try:
    from .anthropic_provider import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from .ollama_provider import OllamaProvider
except ImportError:
    OllamaProvider = None

try:
    from .generic_provider import (
        GenericOpenAIProvider,
        GrokProvider,
        TogetherProvider,
        GroqProvider,
        MistralProvider,
        DeepSeekProvider,
    )
except ImportError:
    GenericOpenAIProvider = None
    GrokProvider = None
    TogetherProvider = None
    GroqProvider = None
    MistralProvider = None
    DeepSeekProvider = None

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
