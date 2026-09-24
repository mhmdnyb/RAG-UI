"""
The only place concrete implementations are imported.

The API and the worker both build from here so they cannot drift apart.
Imports are lazy to keep llama-index and torch out of import time.
"""

from functools import lru_cache

from app.common.logger import get_logger
from app.orchestrator.pipeline import QueryOrchestrator

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def build_orchestrator() -> QueryOrchestrator:
    from app.common.config import settings
    from app.common.database import get_engine
    from app.embedding.service import EmbeddingService
    from app.llm.service import LLMService
    from app.query_router.router import QueryRouter
    from app.retrieval.reranker.reranker import Reranker
    from app.retrieval.sql_pipeline.retriever import SQLRetriever
    from app.retrieval.text_pipeline.retriever import TextRetriever

    engine = get_engine(settings.database_url)
    embedder = EmbeddingService()

    orchestrator = QueryOrchestrator(
        retrievers={
            "sql": SQLRetriever(engine=engine),
            "text": TextRetriever(embedder=embedder),
        },
        router=QueryRouter(),
        reranker=Reranker(),
        llm=LLMService(),
    )
    orchestrator.embedder = embedder
    logger.info("Orchestrator built")
    return orchestrator


async def warm_up(orchestrator: QueryOrchestrator) -> None:
    """Load the embedding model before the first question. Raises on failure."""
    embedder = getattr(orchestrator, "embedder", None)
    if embedder is not None:
        await embedder.warm_up()
