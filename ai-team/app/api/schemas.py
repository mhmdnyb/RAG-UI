"""
Wire contract with Core Service.

Renaming or adding a field here breaks the Java side — Jackson rejects
unknown properties by default. Coordinate before touching it.
"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.common.config import settings

# Stripped before the length check, so a whitespace-only question is a 422.
Question = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=settings.max_question_length,
    ),
]


class QueryRequest(BaseModel):
    conversationId: str = Field(min_length=1, max_length=64)
    question: Question


class QueryAckResponse(BaseModel):
    status: str = "OK"


class SourceItem(BaseModel):
    document: str
    page: int | None = None


class CallbackPayload(BaseModel):
    conversationId: str
    answer: str
    sources: list[SourceItem]


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "rag"


class ReadyResponse(BaseModel):
    status: str
    database: str
    queue: str


class RegulationsUploadResponse(BaseModel):
    status: str = "success"
    filename: str
    parent_articles_count: int
    child_chunks_count: int
    cleared_existing: bool


class PreEmbeddedArticleItem(BaseModel):
    id: str
    section: str
    title: str
    full_text: str


class PreEmbeddedChunkItem(BaseModel):
    id: str
    text: str
    metadata: dict = Field(default_factory=dict)
    embedding: list[float]


class PreEmbeddedImportRequest(BaseModel):
    version: str = "1.0"
    embedding_model: str = "BAAI/bge-m3"
    parent_articles: list[PreEmbeddedArticleItem]
    chunks: list[PreEmbeddedChunkItem]
    clear_existing: bool = True


class PreEmbeddedImportResponse(BaseModel):
    status: str = "success"
    parent_articles_count: int
    child_chunks_count: int
    cleared_existing: bool
