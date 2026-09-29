"""
    uvicorn --factory app.server:create_app --reload --port 8000

This process authenticates, validates and enqueues. It does not load
models and does not run the pipeline — that is the worker's job.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware import RequestIdMiddleware
from app.api.routes import create_router
from app.common.config import settings, validate_settings
from app.common.logger import get_logger, setup_logging
from app.orchestrator.pipeline import QueryOrchestrator

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.worker.broker import broker

    logger.info(
        f"RAG service starting (env={settings.environment}, "
        f"queue={'redis' if settings.use_queue else 'in-process'})"
    )
    # With the in-process broker this also builds and warms the pipeline,
    # because then this process is the worker too.
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()
    from app.common.database import dispose_engine

    dispose_engine()
    logger.info("RAG service stopped")


def create_app(orchestrator: QueryOrchestrator | None = None) -> FastAPI:
    """`orchestrator` is for tests and in-process mode."""
    setup_logging()
    validate_settings()

    if orchestrator is not None:
        from app.worker.broker import broker

        broker.state.orchestrator = orchestrator

    app = FastAPI(
        title="RAG Service",
        description="University Assistant — Retrieval-Augmented Generation Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(create_router())

    logger.info("RAG application created")
    return app
