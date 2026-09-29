"""
Job queue.

    taskiq worker app.worker.broker:broker --max-async-tasks $MAX_CONCURRENT_JOBS

RedisStreamBroker in production: consumer groups give at-least-once
delivery, so a job whose worker died is handed to another one — which
also means a task can occasionally run twice.
InMemoryBroker for local work without Redis.
"""

from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.common.config import settings, validate_settings
from app.common.logger import get_logger, setup_logging

setup_logging()
validate_settings()

logger = get_logger(__name__)


def _build_broker() -> AsyncBroker:
    if not settings.use_queue:
        logger.warning("USE_QUEUE=false — running jobs in-process (development only)")
        return InMemoryBroker(max_async_tasks=settings.max_concurrent_jobs)

    return RedisStreamBroker(
        url=settings.redis_url,
        queue_name=settings.queue_name,
        consumer_group_name=settings.queue_name,
        # A message unacknowledged for this long is handed to another
        # worker, so it must outlast the slowest task.
        idle_timeout=int(settings.job_idle_timeout_seconds * 1000),
    ).with_result_backend(
        RedisAsyncResultBackend(
            redis_url=settings.redis_url,
            result_ex_time=settings.result_ttl_seconds,
        )
    )


broker = _build_broker()
