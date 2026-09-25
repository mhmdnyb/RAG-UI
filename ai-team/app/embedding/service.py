"""Local embedding model, wrapped as a LlamaIndex adapter."""

from __future__ import annotations

import asyncio
from logging import Logger
from typing import TYPE_CHECKING

from app.common.config import settings
from app.common.exceptions import EmbeddingError
from app.common.interfaces import BaseEmbeddingService
from app.common.logger import get_logger

if TYPE_CHECKING:  # keeps llama-index out of import time
    from llama_index.core.base.embeddings.base import BaseEmbedding


class EmbeddingService(BaseEmbeddingService):
    """
    Adapter over a LlamaIndex embedding model.

    Pass `model` in tests; leave it empty in production and the model is
    loaded lazily, once per process. LlamaIndex code gets the model
    explicitly — `VectorStoreIndex(..., embed_model=await svc.get_model())`
    — never through the global `llama_index.core.Settings`.
    """

    def __init__(
        self,
        model: BaseEmbedding | None = None,
        logger: Logger | None = None,
    ):
        self._logger = logger or get_logger(__name__)
        self._model = model
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(settings.embedding_max_concurrency)

    def _build_model(self) -> BaseEmbedding:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        self._logger.info(
            f"Loading embedding model '{settings.embedding_model}' "
            f"on {settings.embedding_device}"
        )
        return HuggingFaceEmbedding(
            model_name=settings.embedding_model,
            device=settings.embedding_device,
            embed_batch_size=settings.embedding_batch_size,
        )

    async def get_model(self) -> BaseEmbedding:
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    self._model = await asyncio.to_thread(self._build_model)
        return self._model

    async def warm_up(self) -> None:
        """
        Pay the cold-start cost at boot. Raises: a worker whose model does
        not load must fail to start, not report itself ready.
        """
        await self.embed_query("warmup")
        self._logger.info("Embedding model warmed up")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = await self.get_model()
        try:
            async with self._semaphore:
                return await asyncio.to_thread(
                    model.get_text_embedding_batch, texts, show_progress=False
                )
        except Exception as e:
            self._logger.error(f"Embedding failed: {e}", exc_info=True)
            raise EmbeddingError(f"Embedding failed: {e}") from e

    async def embed_query(self, text: str) -> list[float]:
        model = await self.get_model()
        try:
            async with self._semaphore:
                return await asyncio.to_thread(model.get_query_embedding, text)
        except Exception as e:
            self._logger.error(f"Query embedding failed: {e}", exc_info=True)
            raise EmbeddingError(f"Query embedding failed: {e}") from e
