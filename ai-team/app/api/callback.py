"""
Callback client — sends the generated answer back to Core Service.

Implements the POST /rag/callback contract from CORE_SERVICE_INTEGRATION.md.

Owner: Dev 7
"""

import httpx
from logging import Logger

from common.config import settings
from common.exceptions import CallbackError
from common.logger import get_logger
from api.schemas import CallbackPayload, SourceItem


async def send_callback(
    conversation_id: str,
    answer: str,
    sources: list[dict],
    logger: Logger | None = None,
) -> None:
    """
    Send the generated answer to Core Service's /rag/callback endpoint.

    This is called after the orchestrator finishes processing.
    Per the integration spec, this MUST be called even on errors
    (with a user-friendly error message in `answer`).
    """
    _logger = logger or get_logger(__name__)

    callback_url = f"{settings.core_service_url}/rag/callback"
    parsed_sources = []
    if sources:
        for s in sources:
            if isinstance(s, SourceItem):
                parsed_sources.append(s)
            elif isinstance(s, dict):
                parsed_sources.append(SourceItem(**s))

    payload = CallbackPayload(
        conversationId=conversation_id,
        answer=answer,
        sources=parsed_sources,
    )

    headers = {
        "Content-Type": "application/json",
    }
    if settings.rag_callback_token:
        headers["Authorization"] = f"Bearer {settings.rag_callback_token}"

    _logger.info(f"Sending callback for job/conversation={conversation_id}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                callback_url,
                json=payload.model_dump(),
                headers=headers,
            )
            response.raise_for_status()
            _logger.info(
                f"Callback sent successfully for conversation={conversation_id}, "
                f"status={response.status_code}"
            )
    except httpx.HTTPError as e:
        _logger.error(f"Callback failed for conversation={conversation_id}: {e}")
        raise CallbackError(f"Failed to send callback: {e}") from e
