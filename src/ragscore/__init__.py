"""
RAGScore - Generate high-quality QA datasets for RAG evaluation

Usage:
    # Command line
    $ ragscore generate

    # Python API (works in Jupyter/Colab!)
    >>> from ragscore import run_pipeline, quick_test
    >>> run_pipeline()

For more information, see: https://github.com/HZYAI/RagScore
"""

__version__ = "0.6.1"
__author__ = "RAGScore Team"

# Auto-patch asyncio for notebook environments on import
from .ui import patch_asyncio as _patch_asyncio

_patch_asyncio()

# Core functionality
from .data_processing import chunk_text, read_docs
from .evaluation import EvaluationSummary, RAGClient, evaluate_rag, run_evaluation

# Exceptions
from .exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    LLMError,
    MissingAPIKeyError,
    RAGScoreError,
)
from .llm import agenerate_qa_for_chunk, generate_qa_for_chunk
from .pipeline import run_pipeline
from .quick_test import quick_test

__all__ = [
    # Version
    "__version__",
    # Core - Generation
    "run_pipeline",
    "read_docs",
    "chunk_text",
    "generate_qa_for_chunk",
    "agenerate_qa_for_chunk",
    # Core - Evaluation
    "run_evaluation",
    "evaluate_rag",
    "EvaluationSummary",
    "RAGClient",
    # Core - Quick Test (Notebook-friendly)
    "quick_test",
    # Exceptions
    "RAGScoreError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "DocumentProcessingError",
    "LLMError",
]
