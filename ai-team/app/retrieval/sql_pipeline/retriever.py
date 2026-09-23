"""
SQL Retriever — wraps the existing sql_pipeline engine
as a BaseRetriever implementation.

Owner: Dev 1

NOTE: This module delegates to the existing `engine.py` and `schema.py`.
      Those files are NOT modified.
"""

import asyncio
from logging import Logger

from sqlalchemy.engine import Engine

from common.interfaces import BaseRetriever, RetrievalResult
from common.exceptions import RetrievalError
from common.logger import get_logger
from .engine import build_sql_query_engine


class SQLRetriever(BaseRetriever):
    """
    Retrieves data from the university database by converting
    natural-language queries to SQL using LlamaIndex.
    """

    def __init__(self, engine: Engine | None = None, logger: Logger | None = None):
        self._engine = engine
        self._logger = logger or get_logger("rag.sql_retriever")
        self._query_engine = None

    def _get_query_engine(self):
        """Lazy-initialize the LlamaIndex SQL query engine."""
        if self._query_engine is None:
            self._query_engine = build_sql_query_engine()
            self._logger.info("SQL query engine initialized")
        return self._query_engine

    async def retrieve(
        self, query: str, top_k: int = 5
    ) -> list[RetrievalResult]:
        """
        Convert the user's natural-language query to SQL,
        execute it, and return results as RetrievalResult objects.
        """
        self._logger.info(f"SQL retrieval for query: {query[:80]}...")
        try:
            query_engine = self._get_query_engine()

            # LlamaIndex query engine is synchronous — run in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, query_engine.query, query
            )

            return [
                RetrievalResult(
                    content=str(response),
                    source="sql_query",
                    page=None,
                    score=1.0,
                    metadata={"type": "sql"},
                )
            ]
        except Exception as e:
            self._logger.error(f"SQL retrieval failed: {e}")
            raise RetrievalError(f"SQL retrieval failed: {e}") from e
