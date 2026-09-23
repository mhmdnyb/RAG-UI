"""
FastAPI application entry point.

This is the NEW web server entry point for the RAG service.
The original main.py is left completely untouched.

Usage:
    python app/server.py
    # or
    uvicorn app.server:app --reload
"""

import uvicorn
from fastapi import FastAPI

from common.config import settings
from common.logger import setup_logging, get_logger
from common.database import get_engine

from retrieval.sql_pipeline.retriever import SQLRetriever
from retrieval.text_pipeline.retriever import TextRetriever
from retrieval.reranker.reranker import Reranker
from query_router.router import QueryRouter
from llm.service import LLMService
from embedding.service import EmbeddingService
from history.service import ChatHistoryService
from orchestrator.pipeline import QueryOrchestrator
from api.routes import create_router
from api.middleware import AuthMiddleware


def create_app() -> FastAPI:
    """
    Application factory — assembles all modules via dependency injection.

    This is the ONLY place that imports concrete implementations.
    All other files depend only on the abstract interfaces.
    """
    setup_logging()
    logger = get_logger("rag.server")
    logger.info("Creating RAG application...")

    # Initialize shared infrastructure
    engine = get_engine(settings.database_url)

    # Assemble modules (Dependency Injection)
    orchestrator = QueryOrchestrator(
        retrievers={
            "sql": SQLRetriever(engine=engine),
            "text": TextRetriever(),
        },
        router=QueryRouter(),
        reranker=Reranker(),
        llm=LLMService(),
        history=ChatHistoryService(),
    )

    # Create FastAPI app
    app = FastAPI(
        title="RAG Service",
        description="University Assistant — Retrieval-Augmented Generation Service",
        version="1.0.0",
    )

    # Add middleware
    app.add_middleware(AuthMiddleware)

    # Add routes
    app.include_router(create_router(orchestrator))

    logger.info("RAG application created successfully")
    return app


# Create app instance for uvicorn
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.rag_service_port,
        reload=True,
    )
