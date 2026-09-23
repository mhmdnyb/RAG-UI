"""
Embedding Service — generates vector embeddings from text.

Owner: Dev 5

TODO: Implement actual embedding API calls (OpenAI, Sentence-Transformers, etc.).
"""

from logging import Logger

from common.interfaces import BaseEmbeddingService
from common.exceptions import EmbeddingError
from common.logger import get_logger


class EmbeddingService(BaseEmbeddingService):
    """
    Converts text into vector embeddings for similarity search.

    This is a STUB — replace with actual implementation.
    """

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        TODO: Implement embedding generation.

        Expected flow:
        1. Send texts to the embedding model API
        2. Return a list of embedding vectors

        Current behavior: returns empty vectors.
        """
        self._logger.warning("EmbeddingService is a stub — returning empty vectors")
        return [[0.0] for _ in texts]
