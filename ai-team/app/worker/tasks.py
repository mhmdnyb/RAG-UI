"""
Two tasks per question:

    process_query_task  → runs the pipeline, enqueues the result
    deliver_callback_task → posts it to Core

They are separate so a failed or retried callback never re-runs retrieval
and the LLM. Delivery is at-least-once: Core may see the same callback
twice and should deduplicate.
"""

import asyncio

import httpx
from taskiq import TaskiqEvents, TaskiqState

from app.api.callback import send_callback
from app.common.config import settings
from app.common.constants import USER_FACING_ERROR
from app.common.context import set_request_id
from app.common.exceptions import CallbackError
from app.common.logger import get_logger
from app.worker.broker import broker

logger = get_logger(__name__)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def _on_startup(state: TaskiqState) -> None:
    from app.composition import build_orchestrator, warm_up

    state.http = httpx.AsyncClient(timeout=settings.callback_timeout_seconds)

    # Already set means a pipeline was injected (tests, custom entry point).
    if getattr(state, "orchestrator", None) is None:
        state.orchestrator = build_orchestrator()
        await warm_up(state.orchestrator)
    logger.info("Worker ready")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def _on_shutdown(state: TaskiqState) -> None:
    client = getattr(state, "http", None)
    if client is not None:
        await client.aclose()
    from app.common.database import dispose_engine

    dispose_engine()
    logger.info("Worker stopped")


@broker.task(task_name="rag.process_query")
async def process_query_task(
    conversation_id: str, question: str, request_id: str = "-"
) -> str:
    set_request_id(request_id)
    logger.info(f"Job started for conversation={conversation_id}")

    state = broker.state
    orchestrator = getattr(state, "orchestrator", None)
    if orchestrator is None:
        from app.composition import build_orchestrator

        orchestrator = build_orchestrator()

    # Failures become an answer rather than propagating, so this task never
    # raises and is never retried.
    try:
        answer, sources = await asyncio.wait_for(
            orchestrator.process_query(conversation_id, question),
            timeout=settings.pipeline_timeout_seconds,
        )
    except TimeoutError:
        logger.error(f"Pipeline timed out for conversation={conversation_id}")
        answer, sources = USER_FACING_ERROR, []
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        answer, sources = USER_FACING_ERROR, []

    await deliver_callback_task.kiq(conversation_id, answer, sources, request_id)

    logger.info(f"Job finished for conversation={conversation_id}")
    return conversation_id


@broker.task(task_name="rag.deliver_callback")
async def deliver_callback_task(
    conversation_id: str,
    answer: str,
    sources: list[dict],
    request_id: str = "-",
) -> None:
    set_request_id(request_id)
    try:
        await send_callback(
            conversation_id,
            answer,
            sources,
            client=getattr(broker.state, "http", None),
        )
    except CallbackError as e:
        # Retries already happened inside send_callback. Raising would only
        # mark the task failed; there is nothing left to retry here.
        logger.error(f"Callback dropped for conversation={conversation_id}: {e}")
