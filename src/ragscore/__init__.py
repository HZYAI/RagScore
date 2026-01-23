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

__version__ = "0.5.2"
__author__ = "RAGScore Team"

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
    # Exceptions
    "RAGScoreError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "DocumentProcessingError",
    "LLMError",
]
