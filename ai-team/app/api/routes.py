"""
POST /rag/query   accept a question, ACK, process it in the background
GET  /health      liveness
GET  /ready       readiness
"""

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile

from app.api.deps import verify_service_token
from app.api.jobs import dispatch_query
from app.api.schemas import (
    HealthResponse,
    PreEmbeddedImportRequest,
    PreEmbeddedImportResponse,
    QueryAckResponse,
    QueryRequest,
    ReadyResponse,
    RegulationsUploadResponse,
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

    async def _read_text_file(upload_file: UploadFile) -> str:
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Filename missing")
        contents = await upload_file.read()
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400, detail="File must be UTF-8 encoded text"
            ) from None
        if not text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        return text

    @router.post(
        "/rag/regulations/upload",
        response_model=RegulationsUploadResponse,
        dependencies=[Depends(verify_service_token)],
        summary="Upload and ingest regulations document into vector store",
    )
    async def upload_regulations(
        file: UploadFile = File(...),
        clear_existing: bool = Query(
            default=True,
            description="Whether to clear existing regulations before ingesting",
        ),
    ) -> RegulationsUploadResponse:
        from app.retrieval.text_pipeline.ingest import ingest_regulations_text

        text = await _read_text_file(file)
        logger.info(
            f"Ingesting uploaded regulations file: {file.filename} ({len(text)} chars)"
        )
        result = await ingest_regulations_text(text, clear_existing=clear_existing)

        return RegulationsUploadResponse(
            status="success",
            filename=file.filename or "",
            parent_articles_count=result.parent_articles_count,
            child_chunks_count=result.child_chunks_count,
            cleared_existing=result.cleared_existing,
        )

    @router.post(
        "/rag/regulations/import-embedded",
        response_model=PreEmbeddedImportResponse,
        dependencies=[Depends(verify_service_token)],
        summary="Import pre-embedded regulations without running ML models on server",
    )
    async def import_embedded_regulations(
        request: PreEmbeddedImportRequest,
    ) -> PreEmbeddedImportResponse:
        from app.retrieval.text_pipeline.ingest import import_precomputed_regulations

        parents = [p.model_dump() for p in request.parent_articles]
        chunks = [c.model_dump() for c in request.chunks]

        logger.info(
            f"Importing pre-embedded regulations: {len(parents)} parents, "
            f"{len(chunks)} chunks (model={request.embedding_model})"
        )

        result = await import_precomputed_regulations(
            parents, chunks, clear_existing=request.clear_existing
        )

        return PreEmbeddedImportResponse(
            status="success",
            parent_articles_count=result.parent_articles_count,
            child_chunks_count=result.child_chunks_count,
            cleared_existing=result.cleared_existing,
        )

    @router.post(
        "/rag/regulations/import-embedded-file",
        response_model=PreEmbeddedImportResponse,
        dependencies=[Depends(verify_service_token)],
        summary="Upload pre-embedded regulations JSON file without running ML models on server",
    )
    async def import_embedded_regulations_file(
        file: UploadFile = File(...),
        clear_existing: bool = Query(
            default=True,
            description="Whether to clear existing regulations before ingesting",
        ),
    ) -> PreEmbeddedImportResponse:
        from app.retrieval.text_pipeline.ingest import import_precomputed_file_contents

        contents = await file.read()
        try:
            result = await import_precomputed_file_contents(
                contents, clear_existing=clear_existing
            )
        except Exception:
            raise HTTPException(
                status_code=400, detail="Invalid JSON file format"
            ) from None

        return PreEmbeddedImportResponse(
            status="success",
            parent_articles_count=result.parent_articles_count,
            child_chunks_count=result.child_chunks_count,
            cleared_existing=result.cleared_existing,
        )

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
