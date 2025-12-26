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

__version__ = "0.1.2"
__author__ = "RAGScore Team"

# Core functionality
from .pipeline import run_pipeline
from .data_processing import read_docs, chunk_text
from .llm import generate_qa_for_chunk
from .vector_store import build_index, save_index, load_index, retrieve

# Exceptions
from .exceptions import (
    RAGScoreError,
    ConfigurationError,
    MissingAPIKeyError,
    DocumentProcessingError,
    LLMError,
    VectorStoreError,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "run_pipeline",
    "read_docs",
    "chunk_text",
    "generate_qa_for_chunk",
    "build_index",
    "save_index",
    "load_index",
    "retrieve",
    # Exceptions
    "RAGScoreError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "DocumentProcessingError",
    "LLMError",
    "VectorStoreError",
]
