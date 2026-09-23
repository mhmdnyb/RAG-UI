"""
Query Router module — classifies user queries to determine the target retrieval strategy.

Owner: Query Router Developer (Mohammadhosein)

TODO: Implement actual LLM-based query classification.
      (e.g., using OpenRouter / meta-llama/llama-3.1-8b-instruct or OpenAI)
      Target routes:
        - "sql": For questions about classes, schedules, and professors.
        - "text": For questions about university rules, regulations, etc.
        - "all": Fallback or when uncertain.
"""

from logging import Logger

from common.interfaces import BaseQueryRouter, RouteResult
from common.logger import get_logger


class QueryRouter(BaseQueryRouter):
    """
    Classifies incoming user questions into a specific route ("sql", "text", or "all").

    This is a STUB / PLACEHOLDER — to be implemented by the Query Router owner.
    """

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger("rag.query_router")

    async def route(self, query: str) -> RouteResult:
        """
        TODO: Implement LLM routing logic here.

        Expected flow:
        1. Send prompt with system instructions to classification LLM
        2. Parse JSON response: {"route": "sql" | "text"}
        3. Return RouteResult(route=..., question=query)

        Current behavior: stub mode returns route="all" so all retrievers
        are queried by default.
        """
        self._logger.info(
            f"QueryRouter (stub) routing query: {query[:60]}... -> 'all'"
        )
        return RouteResult(route="all", question=query, confidence=1.0)
