"""
POST /rag/query   accept a question, ACK, process it in the background
GET  /health      liveness
GET  /ready       readiness
"""

import asyncio

from fastapi import APIRouter, Depends, Response

from app.api.deps import verify_service_token
from app.api.jobs import dispatch_query
from app.api.schemas import (
    HealthResponse,
    QueryAckResponse,
    QueryRequest,
    ReadyResponse,
)
from app.common.config import settings
from app.common.logger import get_logger

logger = get_logger(__name__)


def create_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/rag/query",
        response_model=QueryAckResponse,
        dependencies=[Depends(verify_service_token)],
        summary="Accept a question and process it asynchronously",
    )
    async def handle_query(request: QueryRequest) -> QueryAckResponse:
        # Length only: questions can carry students' personal data.
        logger.info(
            f"Received query: conversation={request.conversationId}, "
            f"length={len(request.question)}"
        )
        await dispatch_query(request.conversationId, request.question)
        # Core Service compares this against the literal string "OK".
        return QueryAckResponse(status="OK")

    @router.get("/health", response_model=HealthResponse, summary="Liveness")
    async def health_check() -> HealthResponse:
        return HealthResponse()

    @router.get(
        "/ready",
        response_model=ReadyResponse,
        summary="Readiness",
        responses={503: {"model": ReadyResponse}},
    )
    async def readiness_check(response: Response) -> ReadyResponse:
        database = await asyncio.to_thread(_check_database)
        queue = await _check_queue()
        ok = database == "ok" and queue in {"ok", "in-process"}
        # Load balancers only look at the status code.
        if not ok:
            response.status_code = 503
        return ReadyResponse(
            status="ready" if ok else "not_ready",
            database=database,
            queue=queue,
        )

    return router


def _check_database() -> str:
    try:
        from sqlalchemy import text

        from app.common.database import get_engine

        with get_engine(settings.database_url).connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as e:
        logger.warning(f"Readiness: database unreachable ({e})")
        return "unreachable"


async def _check_queue() -> str:
    if not settings.use_queue:
        return "in-process"
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        return "ok"
    except Exception as e:
        logger.warning(f"Readiness: broker unreachable ({e})")
        return "unreachable"
