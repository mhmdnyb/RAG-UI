"""Vector search over the university documents."""

from __future__ import annotations

import asyncio
from logging import Logger
from typing import TYPE_CHECKING

from app.common.exceptions import RetrievalError
from app.common.interfaces import (
    BaseEmbeddingService,
    BaseRetriever,
    RetrievalResult,
)
from app.common.logger import get_logger
from app.retrieval.text_pipeline.vectorstore import (
    DEFAULT_REGULATIONS_TABLE,
    get_vector_store,
)

if TYPE_CHECKING:
    from llama_index.core import VectorStoreIndex
    from llama_index.core.embeddings import BaseEmbedding
    from llama_index.vector_stores.postgres import PGVectorStore

DEFAULT_SOURCE_LABEL = "آیین‌نامه آموزشی"


class TextRetriever(BaseRetriever):
    """Vector search retriever querying regulation chunks from PGVector."""

    def __init__(
        self,
        embedder: BaseEmbeddingService | None = None,
        vector_store: PGVectorStore | None = None,
        index: VectorStoreIndex | None = None,
        table_name: str = DEFAULT_REGULATIONS_TABLE,
        logger: Logger | None = None,
    ):
        self._embedder = embedder
        self._vector_store = vector_store
        self._index = index
        self._table_name = table_name
        self._logger = logger or get_logger(__name__)
        self._lock = asyncio.Lock()

    def _build_vector_store_sync(self) -> PGVectorStore:
        return get_vector_store(self._table_name)

    @staticmethod
    def _build_index_sync(
        vector_store: PGVectorStore, embed_model: BaseEmbedding | None
    ) -> VectorStoreIndex:
        from llama_index.core import VectorStoreIndex

        return VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model,
        )

    async def _get_index(self) -> VectorStoreIndex:
        if self._index is not None:
            return self._index

        async with self._lock:
            if self._index is not None:
                return self._index

            embed_model = None
            if self._embedder is None:
                from app.embedding.service import EmbeddingService

                self._embedder = EmbeddingService()

            if hasattr(self._embedder, "get_model"):
                embed_model = await self._embedder.get_model()

            if self._vector_store is None:
                self._vector_store = await asyncio.to_thread(
                    self._build_vector_store_sync
                )

            self._index = await asyncio.to_thread(
                self._build_index_sync,
                self._vector_store,
                embed_model,
            )
            return self._index

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Search vector database and return top_k matching chunks."""
        clean_query = query.strip() if query else ""
        if not clean_query:
            return []

        try:
            index = await self._get_index()
            retriever = index.as_retriever(similarity_top_k=top_k)
            nodes = await retriever.aretrieve(clean_query)

            results: list[RetrievalResult] = []
            for item in nodes:
                node = getattr(item, "node", item)
                content = (
                    node.get_content()
                    if hasattr(node, "get_content")
                    else str(getattr(node, "text", node))
                )
                score = float(getattr(item, "score", 0.0) or 0.0)
                metadata = dict(getattr(node, "metadata", {}) or {})

                source = (
                    metadata.get("title")
                    or metadata.get("article_id")
                    or DEFAULT_SOURCE_LABEL
                )

                results.append(
                    RetrievalResult(
                        content=content,
                        source=source,
                        score=score,
                        metadata=metadata,
                    )
                )

            return results[:top_k]

        except Exception as e:
            self._logger.error(f"Text retrieval failed: {e}", exc_info=True)
            raise RetrievalError(f"Text retrieval failed: {e}") from e
