"""PGVector store provider for regulations text pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import make_url

from app.common.config import settings

if TYPE_CHECKING:
    from llama_index.vector_stores.postgres import PGVectorStore

DEFAULT_REGULATIONS_TABLE = "regulations_chunks"


def get_vector_store(table_name: str = DEFAULT_REGULATIONS_TABLE) -> PGVectorStore:
    """Build and return a PGVectorStore instance connected to the configured database."""
    from llama_index.vector_stores.postgres import PGVectorStore

    db_url = make_url(settings.database_url)
    return PGVectorStore.from_params(
        database=db_url.database,
        host=db_url.host,
        password=db_url.password,
        port=str(db_url.port or 5432),
        user=db_url.username,
        table_name=table_name,
        embed_dim=settings.embedding_dim,
    )
