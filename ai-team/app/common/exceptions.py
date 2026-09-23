"""
Shared exception hierarchy for the RAG service.

All modules should raise exceptions from this hierarchy
so the API layer and orchestrator can handle them consistently.
"""


class RAGBaseError(Exception):
    """Base exception for all RAG service errors."""
    pass


class RetrievalError(RAGBaseError):
    """Raised when a retrieval pipeline fails (SQL, text, etc.)."""
    pass


class RerankingError(RAGBaseError):
    """Raised when the reranker fails."""
    pass


class LLMError(RAGBaseError):
    """Raised when LLM generation fails (API error, timeout, etc.)."""
    pass


class EmbeddingError(RAGBaseError):
    """Raised when embedding generation fails."""
    pass


class ConfigurationError(RAGBaseError):
    """Raised when required configuration is missing or invalid."""
    pass


class AuthenticationError(RAGBaseError):
    """Raised when API authentication fails."""
    pass


class CallbackError(RAGBaseError):
    """Raised when sending callback to Core Service fails."""
    pass
