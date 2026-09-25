"""Ingestion service for text pipeline regulations."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.common.database import get_engine, get_session
from app.common.logger import get_logger
from app.retrieval.text_pipeline.parser import (
    parse_regulations,
    to_article_models,
    to_text_nodes,
)
from app.retrieval.text_pipeline.schema import Base, RegulationArticle
from app.retrieval.text_pipeline.vectorstore import get_vector_store

if TYPE_CHECKING:
    from llama_index.core.embeddings import BaseEmbedding
    from llama_index.vector_stores.postgres import PGVectorStore

logger = get_logger(__name__)


@dataclass
class IngestionResult:
    parent_articles_count: int
    child_chunks_count: int
    cleared_existing: bool


def _clear_vector_store(vector_store: PGVectorStore) -> None:
    try:
        vector_store.clear()
    except Exception as e:
        logger.warning(f"Failed to clear existing vector store entries: {e}")


def _save_articles(articles: list[RegulationArticle], clear_existing: bool) -> None:
    session = get_session()
    try:
        if clear_existing:
            session.query(RegulationArticle).delete()
        for article in articles:
            if clear_existing:
                session.add(article)
            else:
                session.merge(article)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_schema() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def _sync_ingest(
    text: str, clear_existing: bool, embed_model: BaseEmbedding | None
) -> IngestionResult:
    from llama_index.core import StorageContext, VectorStoreIndex

    _ensure_schema()
    vector_store = get_vector_store()

    if clear_existing:
        _clear_vector_store(vector_store)

    parsed_articles = parse_regulations(text)
    article_models = to_article_models(parsed_articles)
    all_children_nodes = to_text_nodes(parsed_articles)

    _save_articles(article_models, clear_existing=clear_existing)

    if all_children_nodes:
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex(
            nodes=all_children_nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=False,
        )

    return IngestionResult(
        parent_articles_count=len(article_models),
        child_chunks_count=len(all_children_nodes),
        cleared_existing=clear_existing,
    )


async def ingest_regulations_text(
    text: str,
    clear_existing: bool = True,
    embedder: Any = None,
) -> IngestionResult:
    """Parse and index regulations text into PostgreSQL and PGVector asynchronously."""
    if embedder is None:
        from app.embedding.service import EmbeddingService

        embedder = EmbeddingService()

    embed_model = None
    if hasattr(embedder, "get_model"):
        embed_model = await embedder.get_model()

    return await asyncio.to_thread(_sync_ingest, text, clear_existing, embed_model)


def _sync_import_precomputed(
    parent_articles: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    clear_existing: bool,
) -> IngestionResult:
    from llama_index.core.schema import TextNode

    _ensure_schema()
    vector_store = get_vector_store()

    if clear_existing:
        _clear_vector_store(vector_store)

    article_models = [
        RegulationArticle(
            id=p["id"],
            section=p.get("section", ""),
            title=p.get("title", ""),
            full_text=p["full_text"],
        )
        for p in parent_articles
    ]
    _save_articles(article_models, clear_existing=clear_existing)

    nodes = [
        TextNode(
            id_=c["id"],
            text=c["text"],
            metadata=dict(c.get("metadata", {})),
            embedding=list(c["embedding"]),
        )
        for c in chunks
    ]

    if nodes:
        vector_store.add(nodes)

    return IngestionResult(
        parent_articles_count=len(parent_articles),
        child_chunks_count=len(nodes),
        cleared_existing=clear_existing,
    )


async def import_precomputed_regulations(
    parent_articles: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    clear_existing: bool = True,
) -> IngestionResult:
    """Insert pre-embedded articles and chunks directly into database without running ML inference."""
    return await asyncio.to_thread(
        _sync_import_precomputed, parent_articles, chunks, clear_existing
    )


async def import_precomputed_file_contents(
    file_bytes: bytes,
    clear_existing: bool = True,
) -> IngestionResult:
    """Parse a pre-embedded regulations JSON file and store into database."""
    data = json.loads(file_bytes.decode("utf-8"))
    parents = list(data.get("parent_articles", []))
    chunks = list(data.get("chunks", []))
    return await import_precomputed_regulations(
        parents, chunks, clear_existing=clear_existing
    )
