"""Cross-Encoder reranking for retrieved candidate documents."""

from __future__ import annotations

import asyncio
import math
from logging import Logger
from typing import Any

from app.common.config import settings
from app.common.exceptions import RerankingError
from app.common.interfaces import BaseReranker, RetrievalResult
from app.common.logger import get_logger


class Reranker(BaseReranker):
    """
    Cross-encoder reranker scoring (query, chunk) pairs.

    Applies sigmoid transformation to logits to produce probability scores,
    sorts descending, filters by score threshold, and optionally expands
    chunks to parent documents (Small-to-Big retrieval) if parent metadata is present.
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        score_threshold: float | None = None,
        expand_parent: bool = True,
        model: Any | None = None,
        logger: Logger | None = None,
    ):
        self._logger = logger or get_logger(__name__)
        self._model_name = model_name or getattr(
            settings, "reranker_model", "BAAI/bge-reranker-v2-m3"
        )
        self._device = device or getattr(settings, "reranker_device", "cpu")
        self._batch_size = (
            batch_size
            if batch_size is not None
            else getattr(settings, "reranker_batch_size", 16)
        )
        self._score_threshold = (
            score_threshold
            if score_threshold is not None
            else getattr(settings, "reranker_score_threshold", 0.0)
        )
        self._expand_parent = expand_parent
        self._model = model
        self._lock = asyncio.Lock()

    def _get_model_sync(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import CrossEncoder

            device = self._device
            if device == "cpu":
                try:
                    import torch

                    if torch.cuda.is_available():
                        device = "cuda"
                except ImportError:
                    pass

            self._logger.info(f"Loading CrossEncoder: {self._model_name} on {device}")
            self._model = CrossEncoder(
                self._model_name,
                max_length=512,
                device=device,
            )
            return self._model
        except Exception as e:
            self._logger.warning(
                f"Failed to load CrossEncoder ({e}). Reranker will fall back to raw results."
            )
            return None

    async def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        async with self._lock:
            if self._model is not None:
                return self._model
            return await asyncio.to_thread(self._get_model_sync)

    def _predict_sync(self, model: Any, pairs: list[list[str]]) -> Any:
        try:
            return model.predict(pairs, batch_size=self._batch_size)
        except TypeError:
            return model.predict(pairs)

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        """Rerank candidates using cross-encoder and update relevance scores."""
        if not results:
            return []

        clean_query = query.strip() if query else ""
        if not clean_query:
            return results[:top_k]

        try:
            model = await self._get_model()
            if model is None:
                return results[:top_k]
            pairs = [[clean_query, r.content] for r in results]

            raw_scores = await asyncio.to_thread(self._predict_sync, model, pairs)

            # Update scores with calibrated probabilities using standard library math
            for item, raw_score in zip(results, raw_scores, strict=False):
                s = float(raw_score)
                if s >= 0:
                    item.score = 1.0 / (1.0 + math.exp(-s))
                else:
                    item.score = math.exp(s) / (1.0 + math.exp(s))

            # Sort descending by score
            ranked = sorted(results, key=lambda x: x.score, reverse=True)

            # Filter by relevance threshold
            if self._score_threshold > 0.0:
                filtered = [r for r in ranked if r.score >= self._score_threshold]
                # If threshold filters all, keep at least the top result
                ranked = filtered if filtered else ranked[:1]

            # Parent-Document Expansion (Small-to-Big)
            if not self._expand_parent:
                return ranked[:top_k]

            expanded_results: list[RetrievalResult] = []
            seen_parents: set[str] = set()

            for r in ranked:
                parent_id = r.metadata.get("parent_id") or r.metadata.get("article_id")
                parent_text = r.metadata.get("parent_full_text")

                if parent_id and parent_text:
                    if parent_id not in seen_parents:
                        seen_parents.add(parent_id)
                        expanded_r = RetrievalResult(
                            content=parent_text,
                            source=r.metadata.get("parent_title") or r.source,
                            page=r.page,
                            score=r.score,
                            metadata=r.metadata,
                        )
                        expanded_results.append(expanded_r)
                else:
                    expanded_results.append(r)

            return expanded_results[:top_k]

        except Exception as exc:
            self._logger.warning(
                f"Reranking failed ({exc}), falling back to raw order",
                exc_info=True,
            )
            return results[:top_k]
