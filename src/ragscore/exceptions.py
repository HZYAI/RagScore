"""
RAGScore Custom Exceptions

Provides structured error handling for the RAGScore library.
"""


class RAGScoreError(Exception):
    """Base exception for all RAGScore errors."""

    pass


# Configuration Errors
class ConfigurationError(RAGScoreError):
    """Raised when there's a configuration problem."""

    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when a required API key is not set."""

    def __init__(self, provider: str, env_var: str):
        self.provider = provider
        self.env_var = env_var
        super().__init__(
            f"{provider} API key not found.\n"
            f"Set it via environment variable: export {env_var}='your-key'\n"
            f"Or in your .env file: {env_var}=your-key"
        )


class InvalidProviderError(ConfigurationError):
    """Raised when an invalid LLM provider is specified."""

    def __init__(self, provider: str, valid_providers: list):
        self.provider = provider
        self.valid_providers = valid_providers
        super().__init__(
            f"Invalid provider '{provider}'. Valid providers are: {', '.join(valid_providers)}"
        )


# Document Processing Errors
class DocumentProcessingError(RAGScoreError):
    """Raised when document processing fails."""

    pass


class UnsupportedFileTypeError(DocumentProcessingError):
    """Raised when a file type is not supported."""

    def __init__(self, file_path: str, supported_types: list):
        self.file_path = file_path
        self.supported_types = supported_types
        super().__init__(
            f"Unsupported file type: {file_path}\nSupported types: {', '.join(supported_types)}"
        )


class EmptyDocumentError(DocumentProcessingError):
    """Raised when a document has no extractable content."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"No text content could be extracted from: {file_path}")


# LLM Errors
class LLMError(RAGScoreError):
    """Base exception for LLM-related errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int = None):
        self.provider = provider
        self.retry_after = retry_after
        msg = f"Rate limit exceeded for {provider}."
        if retry_after:
            msg += f" Retry after {retry_after} seconds."
        super().__init__(msg)


class LLMResponseError(LLMError):
    """Raised when LLM returns an invalid response."""

    pass


# Assessment Errors
class AssessmentError(RAGScoreError):
    """Base exception for assessment errors."""

    pass


class EndpointConnectionError(AssessmentError):
    """Raised when connection to RAG endpoint fails."""

    def __init__(self, endpoint_url: str, reason: str = None):
        self.endpoint_url = endpoint_url
        self.reason = reason
        msg = f"Failed to connect to RAG endpoint: {endpoint_url}"
        if reason:
            msg += f"\nReason: {reason}"
        super().__init__(msg)


class AuthenticationError(AssessmentError):
    """Raised when authentication to RAG endpoint fails."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        super().__init__(f"Authentication failed for endpoint: {endpoint_url}")


class QAFileNotFoundError(AssessmentError):
    """Raised when the QA pairs file doesn't exist."""

    def __init__(self, qa_path: str):
        self.qa_path = qa_path
        super().__init__(
            f"QA pairs file not found: {qa_path}\nRun 'ragscore generate' first to create QA pairs."
        )
