"""
Routes a question to the SQL pipeline, the text pipeline, or both.

  sql  — classes, schedules, professors
  text — rules, regulations, documents
  all  — fallback when uncertain
"""

from logging import Logger

from app.common.interfaces import BaseQueryRouter, RouteResult
from app.common.logger import get_logger


class QueryRouter(BaseQueryRouter):
    """Stub: routes everything to "all"."""

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)

    async def route(self, query: str) -> RouteResult:
        # TODO(#1): LLM-based classification
        self._logger.info(f"Routing (stub): {query[:60]} -> 'all'")
        return RouteResult(route="all", question=query, confidence=1.0)
