"""
Query Orchestrator — the central pipeline that coordinates all modules.

This module uses Dependency Injection: it receives all module instances
via the constructor and does NOT import any concrete implementations.

Changes to this file should be reviewed by the team lead.
"""

from logging import Logger

from common.interfaces import (
    BaseRetriever,
    BaseReranker,
    BaseLLMService,
    BaseChatHistory,
    BaseQueryRouter,
    RetrievalResult,
)
from common.exceptions import RAGBaseError
from common.logger import get_logger


class QueryOrchestrator:
    """
    Orchestrates the full RAG pipeline:
    route → retrieve → rerank → generate → save history.

    All dependencies are injected via the constructor.
    """

    def __init__(
        self,
        retrievers: list[BaseRetriever] | dict[str, BaseRetriever],
        reranker: BaseReranker,
        llm: BaseLLMService,
        history: BaseChatHistory | None = None,
        router: BaseQueryRouter | None = None,
        logger: Logger | None = None,
    ):
        self.retrievers = retrievers
        self.reranker = reranker
        self.llm = llm
        self.history = history
        self.router = router
        self.logger = logger or get_logger(__name__)

    async def process_query(
        self, conversation_id: str, question: str
    ) -> tuple[str, list[dict]]:
        """
        Run the full RAG pipeline for a user question.

        Returns:
            (answer, sources) where sources is a list of
            {"document": str, "page": int} dicts.
        """
        self.logger.info(
            f"Processing query for job/conversation={conversation_id}: "
            f"{question[:80]}..."
        )

        try:
            # 1. Determine target retrievers (via Router if provided)
            target_retrievers: list[BaseRetriever] = []
            if self.router is not None and isinstance(self.retrievers, dict):
                try:
                    route_result = await self.router.route(question)
                    target_route = (
                        route_result.route.lower()
                        if hasattr(route_result, "route")
                        else str(route_result).lower()
                    )
                    self.logger.info(f"Router selected route: '{target_route}'")
                    if target_route in self.retrievers:
                        target_retrievers = [self.retrievers[target_route]]
                    else:
                        target_retrievers = list(self.retrievers.values())
                except Exception as e:
                    self.logger.warning(
                        f"Routing failed ({e}), falling back to all retrievers"
                    )
                    target_retrievers = list(self.retrievers.values())
            elif isinstance(self.retrievers, dict):
                target_retrievers = list(self.retrievers.values())
            else:
                target_retrievers = list(self.retrievers)

            # 2. Retrieve from target retrievers
            all_results: list[RetrievalResult] = []
            for retriever in target_retrievers:
                try:
                    results = await retriever.retrieve(question)
                    all_results.extend(results)
                    self.logger.info(
                        f"{retriever.__class__.__name__} returned "
                        f"{len(results)} results"
                    )
                except RAGBaseError as e:
                    self.logger.warning(
                        f"{retriever.__class__.__name__} failed: {e}, "
                        f"continuing with other retrievers"
                    )

            # 3. Rerank combined results
            if all_results:
                ranked = await self.reranker.rerank(question, all_results)
            else:
                ranked = []

            # 4. Generate answer via LLM (Stateless — no chat history)
            answer = await self.llm.generate(question, ranked)

            # 5. Format sources for the API response
            sources = [
                {"document": r.source, "page": r.page or 0}
                for r in ranked
            ]

            self.logger.info(
                f"Query processed successfully for conversation={conversation_id}"
            )
            return answer, sources

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            # Always return a user-friendly message (never leave the user hanging)
            error_msg = (
                "متأسفانه در پردازش سوال شما خطایی رخ داد. "
                "لطفاً دوباره تلاش کنید."
            )  # "An error occurred processing your question. Please try again."
            return error_msg, []
