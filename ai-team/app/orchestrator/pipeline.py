"""
The RAG pipeline: route, retrieve, rerank, generate.

Dependencies are injected; nothing concrete is imported here.
Changes should be reviewed by the team lead.
"""

import asyncio
from dataclasses import dataclass, field
from logging import Logger

from app.common.config import settings
from app.common.constants import NO_RESULTS_FOUND
from app.common.exceptions import RetrievalError
from app.common.interfaces import (
    BaseChatHistory,
    BaseLLMService,
    BaseQueryRouter,
    BaseReranker,
    BaseRetriever,
    RetrievalResult,
)
from app.common.logger import get_logger

# Standard constant for Reciprocal Rank Fusion.
_RRF_K = 60


@dataclass
class _Outcome:
    retriever: str
    ok: bool
    results: list[RetrievalResult] = field(default_factory=list)


def _fuse(batches: list[list[RetrievalResult]]) -> list[RetrievalResult]:
    """
    Reciprocal Rank Fusion. Scores from different retrievers are not on
    the same scale, so only each result's rank inside its own batch counts.
    """
    fused: dict[tuple, tuple[float, RetrievalResult]] = {}
    for batch in batches:
        ordered = sorted(batch, key=lambda r: r.score, reverse=True)
        for rank, result in enumerate(ordered, start=1):
            key = (result.source, result.page, result.content)
            prev_score, _ = fused.get(key, (0.0, result))
            fused[key] = (prev_score + 1.0 / (_RRF_K + rank), result)
    ranked = sorted(fused.values(), key=lambda item: item[0], reverse=True)
    return [result for _, result in ranked]


class QueryOrchestrator:
    def __init__(
        self,
        retrievers: list[BaseRetriever] | dict[str, BaseRetriever],
        reranker: BaseReranker,
        llm: BaseLLMService,
        history: BaseChatHistory | None = None,
        router: BaseQueryRouter | None = None,
        logger: Logger | None = None,
    ):
        # `history` is unused for now; the slot exists so chat history can
        # be added later without changing this signature.
        self.retrievers = retrievers
        self.reranker = reranker
        self.llm = llm
        self.history = history
        self.router = router
        self.logger = logger or get_logger(__name__)

    async def _select_retrievers(self, question: str) -> list[BaseRetriever]:
        if not isinstance(self.retrievers, dict):
            return list(self.retrievers)

        if self.router is None:
            return list(self.retrievers.values())

        try:
            result = await self.router.route(question)
            route = getattr(result, "route", str(result)).lower()
            self.logger.info(f"Router selected route: '{route}'")
            if route in self.retrievers:
                return [self.retrievers[route]]
        except Exception as e:
            self.logger.warning(
                f"Routing failed ({e}), falling back to all retrievers",
                exc_info=True,
            )
        return list(self.retrievers.values())

    async def _run_one(self, retriever: BaseRetriever, question: str) -> _Outcome:
        name = retriever.__class__.__name__
        try:
            results = await asyncio.wait_for(
                retriever.retrieve(question, top_k=settings.retrieval_top_k),
                timeout=settings.retriever_timeout_seconds,
            )
            self.logger.info(f"{name} returned {len(results)} results")
            return _Outcome(name, ok=True, results=list(results))
        except TimeoutError:
            self.logger.warning(f"{name} timed out, continuing without it")
        except Exception as e:
            # Broad on purpose: one broken retriever must not sink the query.
            self.logger.warning(f"{name} failed: {e}", exc_info=True)
        return _Outcome(name, ok=False)

    async def process_query(
        self, conversation_id: str, question: str
    ) -> tuple[str, list[dict]]:
        """
        Returns (answer, sources).

        Errors propagate: the caller decides what the user is told.
        """
        self.logger.info(f"Processing query for conversation={conversation_id}")

        targets = await self._select_retrievers(question)

        outcomes = await asyncio.gather(*(self._run_one(r, question) for r in targets))
        all_results = _fuse([o.results for o in outcomes if o.ok])

        # "Nothing found" is only true if every search actually ran.
        failed = [o.retriever for o in outcomes if not o.ok]
        if failed and not all_results:
            raise RetrievalError(
                f"No results and retrievers failed: {', '.join(failed)}"
            )

        ranked: list[RetrievalResult] = []
        if all_results:
            try:
                ranked = await self.reranker.rerank(
                    question, all_results, top_k=settings.reranker_top_k
                )
            except Exception as e:
                self.logger.warning(
                    f"Reranker failed ({e}), using fused order",
                    exc_info=True,
                )
                ranked = all_results[: settings.reranker_top_k]

        if not ranked:
            self.logger.info("No results retrieved for this query")
            return NO_RESULTS_FOUND, []

        answer = await self.llm.generate(question, ranked)
        sources = [{"document": r.source, "page": r.page} for r in ranked]

        self.logger.info(
            f"Query processed successfully for conversation={conversation_id}"
        )
        return answer, sources
