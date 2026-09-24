"""Vector search over the university documents."""

from logging import Logger

from app.common.interfaces import (
    BaseEmbeddingService,
    BaseRetriever,
    RetrievalResult,
)
from app.common.logger import get_logger


class TextRetriever(BaseRetriever):
    """Stub: returns nothing."""

    def __init__(
        self,
        embedder: BaseEmbeddingService | None = None,
        logger: Logger | None = None,
    ):
        self._embedder = embedder
        self._logger = logger or get_logger(__name__)

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        # TODO(#4): embed the query with self._embedder.embed_query(),
        # then search pgvector.
        self._logger.warning("TextRetriever is a stub — returning no results")
        return []
