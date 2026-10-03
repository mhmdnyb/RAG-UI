"""Global exception handlers, so nothing fails silently with a bare 500."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.context import get_request_id
from app.common.exceptions import RAGBaseError
from app.common.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        body = await request.body()
        logger.error(f"Validation error on {request.url.path}: {exc.errors()} - raw body: {body}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(RAGBaseError)
    async def _rag_error(request: Request, exc: RAGBaseError):
        logger.error(f"RAG error on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal RAG service error",
                "type": exc.__class__.__name__,
                "requestId": get_request_id(),
            },
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "requestId": get_request_id(),
            },
        )
