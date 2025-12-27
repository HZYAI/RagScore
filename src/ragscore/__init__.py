"""
RAGScore - Generate high-quality QA datasets for RAG evaluation

Usage:
    # Command line
    $ ragscore generate

    # Python API
    >>> from ragscore import run_pipeline
    >>> run_pipeline()

For more information, see: https://github.com/ragscore/ragscore
"""

__version__ = "0.2.1"
__author__ = "RAGScore Team"

# Core functionality
from .data_processing import chunk_text, read_docs

# Exceptions
from .exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    LLMError,
    MissingAPIKeyError,
    RAGScoreError,
)
from .llm import generate_qa_for_chunk
from .pipeline import run_pipeline

__all__ = [
    # Version
    "__version__",
    # Core
    "run_pipeline",
    "read_docs",
    "chunk_text",
    "generate_qa_for_chunk",
    # Exceptions
    "RAGScoreError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "DocumentProcessingError",
    "LLMError",
]
