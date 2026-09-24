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
