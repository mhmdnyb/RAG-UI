"""
Delivers the answer back to Core Service.

    POST {CORE_SERVICE_URL}/rag/callback
    {"conversationId": str, "answer": str,
     "sources": [{"document": str, "page": int|null}]}

Every accepted question must produce a callback, success or failure —
otherwise the student's message stays PROCESSING forever. Delivery is
at-least-once, not exactly-once.
"""

import asyncio
from logging import Logger

import httpx

from app.api.schemas import CallbackPayload, SourceItem
from app.common.config import settings
from app.common.exceptions import CallbackError
from app.common.logger import get_logger


def _build_payload(
    conversation_id: str, answer: str, sources: list[dict] | None
) -> CallbackPayload:
    items: list[SourceItem] = []
    for s in sources or []:
        items.append(s if isinstance(s, SourceItem) else SourceItem(**s))
    return CallbackPayload(conversationId=conversation_id, answer=answer, sources=items)


async def send_callback(
    conversation_id: str,
    answer: str,
    sources: list[dict] | None = None,
    client: httpx.AsyncClient | None = None,
    logger: Logger | None = None,
) -> None:
    """Retries with exponential backoff. Raises CallbackError if it never lands."""
    _logger = logger or get_logger(__name__)

    url = f"{settings.core_service_url.rstrip('/')}/rag/callback"
    payload = _build_payload(conversation_id, answer, sources)

    headers = {"Content-Type": "application/json"}
    if settings.rag_callback_token:
        headers["Authorization"] = f"Bearer {settings.rag_callback_token}"

    attempts = max(1, settings.callback_max_attempts)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            if client is not None:
                response = await client.post(
                    url, json=payload.model_dump(), headers=headers
                )
            else:
                async with httpx.AsyncClient(
                    timeout=settings.callback_timeout_seconds
                ) as owned:
                    response = await owned.post(
                        url, json=payload.model_dump(), headers=headers
                    )
            response.raise_for_status()
            _logger.info(
                f"Callback delivered for conversation={conversation_id} "
                f"(attempt {attempt}, status={response.status_code})"
            )
            return
        except httpx.HTTPStatusError as e:
            last_error = e
            # 4xx: Core cannot accept this body, resending it won't help.
            if 400 <= e.response.status_code < 500:
                _logger.error(
                    f"Callback rejected with {e.response.status_code} for "
                    f"conversation={conversation_id}; not retrying"
                )
                break
            _logger.warning(
                f"Callback attempt {attempt}/{attempts} failed "
                f"({e.response.status_code}) for conversation={conversation_id}"
            )
        except httpx.HTTPError as e:
            last_error = e
            _logger.warning(
                f"Callback attempt {attempt}/{attempts} failed "
                f"({e}) for conversation={conversation_id}"
            )

        if attempt < attempts:
            await asyncio.sleep(2 ** (attempt - 1))

    raise CallbackError(
        f"Failed to deliver callback for conversation={conversation_id}: {last_error}"
    )
