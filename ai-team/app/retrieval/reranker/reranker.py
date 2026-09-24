"""Re-scores retrieval results before they reach the LLM."""

from logging import Logger

from app.common.interfaces import BaseReranker, RetrievalResult
from app.common.logger import get_logger


class Reranker(BaseReranker):
    """Stub: passes results through, truncated to top_k."""

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        # TODO(#3): cross-encoder scoring
        self._logger.warning("Reranker is a stub — no reranking applied")
        return results[:top_k]
