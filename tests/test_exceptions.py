"""Tests for the exceptions module."""

from ragscore.exceptions import (
    AssessmentError,
    ConfigurationError,
    DocumentProcessingError,
    EmptyDocumentError,
    EndpointConnectionError,
    InvalidProviderError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    MissingAPIKeyError,
    QAFileNotFoundError,
    RAGScoreError,
    UnsupportedFileTypeError,
)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_base_exception(self):
        """All exceptions should inherit from RAGScoreError."""
        assert issubclass(ConfigurationError, RAGScoreError)
        assert issubclass(DocumentProcessingError, RAGScoreError)
        assert issubclass(LLMError, RAGScoreError)
        assert issubclass(AssessmentError, RAGScoreError)

    def test_configuration_exceptions(self):
        """Test configuration exception hierarchy."""
        assert issubclass(MissingAPIKeyError, ConfigurationError)
        assert issubclass(InvalidProviderError, ConfigurationError)

    def test_document_exceptions(self):
        """Test document processing exception hierarchy."""
        assert issubclass(UnsupportedFileTypeError, DocumentProcessingError)
        assert issubclass(EmptyDocumentError, DocumentProcessingError)

    def test_llm_exceptions(self):
        """Test LLM exception hierarchy."""
        assert issubclass(LLMConnectionError, LLMError)
        assert issubclass(LLMRateLimitError, LLMError)


class TestMissingAPIKeyError:
    """Test MissingAPIKeyError."""

    def test_message_format(self):
        """Test error message includes provider and env var."""
        err = MissingAPIKeyError("OpenAI", "OPENAI_API_KEY")

        assert "OpenAI" in str(err)
        assert "OPENAI_API_KEY" in str(err)
        assert err.provider == "OpenAI"
        assert err.env_var == "OPENAI_API_KEY"

    def test_message_includes_instructions(self):
        """Test error message includes helpful instructions."""
        err = MissingAPIKeyError("DashScope", "DASHSCOPE_API_KEY")
        msg = str(err)

        assert "export" in msg.lower() or "set" in msg.lower()
        assert ".env" in msg


class TestInvalidProviderError:
    """Test InvalidProviderError."""

    def test_message_format(self):
        """Test error message includes invalid and valid providers."""
        err = InvalidProviderError("invalid", ["openai", "dashscope"])

        assert "invalid" in str(err)
        assert "openai" in str(err)
        assert "dashscope" in str(err)
        assert err.provider == "invalid"
        assert err.valid_providers == ["openai", "dashscope"]


class TestUnsupportedFileTypeError:
    """Test UnsupportedFileTypeError."""

    def test_message_format(self):
        """Test error message includes file and supported types."""
        err = UnsupportedFileTypeError("/path/to/file.xyz", [".pdf", ".txt", ".md"])

        assert "file.xyz" in str(err)
        assert ".pdf" in str(err)
        assert err.file_path == "/path/to/file.xyz"


class TestEmptyDocumentError:
    """Test EmptyDocumentError."""

    def test_message_format(self):
        """Test error message includes file path."""
        err = EmptyDocumentError("/path/to/empty.pdf")

        assert "empty.pdf" in str(err)
        assert err.file_path == "/path/to/empty.pdf"


class TestLLMRateLimitError:
    """Test LLMRateLimitError."""

    def test_without_retry_after(self):
        """Test error without retry_after."""
        err = LLMRateLimitError("OpenAI")

        assert "OpenAI" in str(err)
        assert "Rate limit" in str(err)
        assert err.retry_after is None

    def test_with_retry_after(self):
        """Test error with retry_after."""
        err = LLMRateLimitError("OpenAI", retry_after=60)

        assert "60" in str(err)
        assert err.retry_after == 60


class TestEndpointConnectionError:
    """Test EndpointConnectionError."""

    def test_without_reason(self):
        """Test error without reason."""
        err = EndpointConnectionError("http://localhost:5000/query")

        assert "localhost:5000" in str(err)

    def test_with_reason(self):
        """Test error with reason."""
        err = EndpointConnectionError("http://localhost:5000/query", reason="Connection refused")

        assert "Connection refused" in str(err)
        assert err.reason == "Connection refused"


class TestQAFileNotFoundError:
    """Test QAFileNotFoundError."""

    def test_message_format(self):
        """Test error message includes path and instructions."""
        err = QAFileNotFoundError("/output/qa.jsonl")

        assert "qa.jsonl" in str(err)
        assert "ragscore generate" in str(err)
