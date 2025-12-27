"""
Pytest configuration and fixtures for RAGScore tests.
"""

import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# Environment Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def mock_api_keys(monkeypatch):
    """Mock API keys for all tests by default."""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-dashscope-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")


@pytest.fixture
def no_api_keys(monkeypatch):
    """Remove all API keys for testing error handling."""
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)


# ============================================================================
# Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_docs_dir(temp_dir: Path) -> Path:
    """Create a directory with sample documents."""
    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()

    # Create sample text file
    (docs_dir / "sample.txt").write_text(
        "This is a sample document about machine learning. "
        "Machine learning is a subset of artificial intelligence. "
        "It involves training algorithms on data to make predictions. "
        "Deep learning is a type of machine learning using neural networks. "
        "Natural language processing uses machine learning for text analysis."
    )

    # Create sample markdown file
    (docs_dir / "readme.md").write_text(
        "# Sample Documentation\n\n"
        "This is a sample markdown file for testing.\n\n"
        "## Features\n"
        "- Feature one: parsing documents\n"
        "- Feature two: generating questions\n"
        "- Feature three: evaluating answers\n"
    )

    return docs_dir


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    """Create an output directory."""
    out_dir = temp_dir / "output"
    out_dir.mkdir()
    return out_dir


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_text() -> str:
    """Return sample text for testing."""
    return """
    Retrieval-Augmented Generation (RAG) is a technique that combines
    information retrieval with text generation. RAG systems first retrieve
    relevant documents from a knowledge base, then use those documents as
    context for generating responses. This approach helps reduce hallucinations
    and ensures responses are grounded in factual information.

    Key components of a RAG system include:
    1. A document store or knowledge base
    2. An embedding model for semantic search
    3. A vector database like FAISS or Pinecone
    4. A large language model for generation

    RAG is particularly useful for question-answering systems where accuracy
    is critical and the knowledge base is frequently updated.
    """


@pytest.fixture
def sample_qa_pairs() -> list:
    """Return sample QA pairs for testing."""
    return [
        {
            "id": "qa-001",
            "question": "What is RAG?",
            "answer": "RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with text generation.",
            "rationale": "Directly stated in the first sentence.",
            "support_span": "Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with text generation.",
            "doc_id": "doc-001",
            "chunk_id": "0",
            "source_path": "/docs/sample.txt",
            "difficulty": "easy",
        },
        {
            "id": "qa-002",
            "question": "What are the key components of a RAG system?",
            "answer": "The key components include a document store, embedding model, vector database, and large language model.",
            "rationale": "Listed explicitly in the text.",
            "support_span": "Key components of a RAG system include: 1. A document store...",
            "doc_id": "doc-001",
            "chunk_id": "0",
            "source_path": "/docs/sample.txt",
            "difficulty": "medium",
        },
    ]


@pytest.fixture
def sample_qa_jsonl(temp_dir: Path, sample_qa_pairs: list) -> Path:
    """Create a sample QA pairs JSONL file."""
    import json

    qa_file = temp_dir / "generated_qas.jsonl"
    with open(qa_file, "w") as f:
        for qa in sample_qa_pairs:
            f.write(json.dumps(qa) + "\n")

    return qa_file


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_llm_response():
    """Return a mock LLM response for QA generation."""
    return {
        "items": [
            {
                "question": "What is machine learning?",
                "answer": "Machine learning is a subset of artificial intelligence.",
                "rationale": "Stated in the document.",
                "support_span": "Machine learning is a subset of artificial intelligence.",
            }
        ]
    }


@pytest.fixture
def mock_dashscope_generation(mock_llm_response):
    """Mock DashScope Generation.call()."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.output = {
        "choices": [{"message": {"content": str(mock_llm_response).replace("'", '"')}}]
    }

    with patch("dashscope.Generation.call", return_value=mock_response) as mock:
        yield mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"items": []}'))]
    mock_response.model = "gpt-4o-mini"
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    mock_response.model_dump.return_value = {"choices": []}

    mock_client.chat.completions.create.return_value = mock_response

    with patch("openai.OpenAI", return_value=mock_client) as mock:
        yield mock


# ============================================================================
# Embedding Fixtures
# ============================================================================


# Embedding mocks removed - no longer needed without vector store


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def mock_config(temp_dir: Path, sample_docs_dir: Path, output_dir: Path):
    """Mock config module with test paths."""
    with patch.multiple(
        "ragscore.config",
        ROOT_DIR=temp_dir,
        DATA_DIR=temp_dir / "data",
        DOCS_DIR=sample_docs_dir,
        OUTPUT_DIR=output_dir,
        INDEX_PATH=output_dir / "index.faiss",
        META_PATH=output_dir / "meta.json",
        GENERATED_QAS_PATH=output_dir / "generated_qas.jsonl",
        DASHSCOPE_API_KEY="test-key",
    ):
        yield
