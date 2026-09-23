"""
FastAPI route handlers.

Implements the endpoints defined in CORE_SERVICE_INTEGRATION.md:
  - POST /rag/query   — receive question, ACK immediately, process in background
  - GET  /health      — health check

Owner: Dev 7
"""

from fastapi import APIRouter, BackgroundTasks

from common.logger import get_logger
from orchestrator.pipeline import QueryOrchestrator
from api.schemas import QueryRequest, QueryAckResponse, HealthResponse
from api.callback import send_callback

logger = get_logger(__name__)


def create_router(orchestrator: QueryOrchestrator) -> APIRouter:
    """
    Factory function that creates a FastAPI router
    with the orchestrator injected.
    """
    router = APIRouter()

    @router.post("/rag/query", response_model=QueryAckResponse)
    async def handle_query(
        request: QueryRequest, background_tasks: BackgroundTasks
    ):
        """
        Receive a question from Core Service.
        - ACK immediately with {"status": "OK"}
        - Process the question in a background task
        - Send the answer via callback when ready
        """
        logger.info(
            f"Received query: conversation={request.conversationId}, "
            f"question={request.question[:80]}..."
        )

        # Schedule background processing (non-blocking)
        background_tasks.add_task(
            _process_and_callback,
            orchestrator,
            request.conversationId,
            request.question,
        )

        # Return immediate ACK (MUST be exactly "OK")
        return QueryAckResponse(status="OK")

    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint for Docker/K8s."""
        return HealthResponse()

    return router


async def _process_and_callback(
    orchestrator: QueryOrchestrator,
    conversation_id: str,
    question: str,
) -> None:
    """
    Background task: process the query through the full RAG pipeline,
    then send the result to Core Service via callback.

    Per the integration spec, this MUST always call the callback —
    even if the pipeline fails (with a user-friendly error message).
    """
    try:
        answer, sources = await orchestrator.process_query(
            conversation_id, question
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        answer = (
            "متأسفانه در پردازش سوال شما خطایی رخ داد. "
            "لطفاً دوباره تلاش کنید."
        )
        sources = []

    # Always send callback to Core Service
    try:
        await send_callback(conversation_id, answer, sources)
    except Exception as e:
        logger.error(
            f"Callback failed for conversation={conversation_id}: {e}",
            exc_info=True,
        )
