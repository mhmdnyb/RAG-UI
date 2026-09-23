"""
Text/Vector Retriever — stub implementation for document-based retrieval.

Owner: Dev 2

TODO: Implement actual vector search using embeddings + pgvector or similar.
"""

from logging import Logger

from common.interfaces import BaseRetriever, RetrievalResult
from common.exceptions import RetrievalError
from common.logger import get_logger


class TextRetriever(BaseRetriever):
    """
    Retrieves relevant text chunks from document embeddings
    using vector similarity search.

    This is a STUB — replace with actual implementation.
    """

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger("rag.text_retriever")

    async def retrieve(
        self, query: str, top_k: int = 5
    ) -> list[RetrievalResult]:
        """
        TODO: Implement vector similarity search.

        Expected flow:
        1. Embed the query using BaseEmbeddingService
        2. Search the vector store for similar chunks
        3. Return top_k results as RetrievalResult objects
        """
        self._logger.warning("TextRetriever is a stub — returning empty results")
        return []
