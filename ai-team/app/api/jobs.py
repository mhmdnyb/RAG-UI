"""Hands a question to the queue."""

from app.common.context import get_request_id
from app.common.logger import get_logger

logger = get_logger(__name__)


async def dispatch_query(conversation_id: str, question: str) -> str:
    from app.worker.tasks import process_query_task

    task = await process_query_task.kiq(conversation_id, question, get_request_id())
    logger.info(
        f"Job enqueued for conversation={conversation_id} (task={task.task_id})"
    )
    return task.task_id
