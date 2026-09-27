"""Answer generation from retrieved context."""

from __future__ import annotations

import os
from logging import Logger
from typing import Any

from app.common.config import settings
from app.common.constants import NO_RESULTS_FOUND
from app.common.exceptions import LLMError
from app.common.interfaces import BaseLLMService, RetrievalResult
from app.common.logger import get_logger

SYSTEM_PROMPT = """تو کارشناس حقوقی و مشاور دقیق آیین‌نامه‌های آموزشی وزارت علوم هستی.

وظایف:
۱. صرفاً بر مبنای مستندات زیر پاسخ مستدل و صریح بده.
۲. در بدنه پاسخ حتماً ماده و تبصره مربوط را ذکر کن.
۳. در پایان پاسخ، بخشی با تیتر «📌 مستندات قانونی استناد شده» ایجاد کن و مواد/تبصره‌ها را لیست کن.
۴. اگر پاسخ در مستندات نیست، بنویس «اطلاعات کافی برای پاسخ به این سؤال در منابع موجود نیست.».

مستندات قانونی:
{context}"""


def _format_context(context: list[RetrievalResult] | str) -> str:
    """Format retrieval results into readable text with document sources."""
    if isinstance(context, str):
        return context.strip()

    parts = []
    for item in context:
        content = item.content.strip()
        if not content:
            continue
        if item.source:
            header = f"[{item.source}"
            if item.page is not None:
                header += f", صفحه {item.page}"
            header += "]"
            parts.append(f"{header}\n{content}")
        else:
            parts.append(content)
    return "\n\n".join(parts)


class LLMService(BaseLLMService):
    """
    LLM service generating answers based on retrieved context.

    Supports custom model, temperature, base_url, max_tokens, or injected client.
    Defaults to settings.llm_* / settings.openai_api_key / GAPGPT_API_KEY.
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        client: Any | None = None,
        logger: Logger | None = None,
    ):
        self._logger = logger or get_logger(__name__)
        self._model = model or settings.resolved_llm_model
        self._temperature = (
            temperature if temperature is not None else settings.llm_temperature
        )
        self._max_tokens = (
            max_tokens if max_tokens is not None else settings.llm_max_tokens
        )
        self._base_url = (
            base_url
            if base_url is not None
            else (settings.resolved_llm_base_url or os.getenv("GAPGPT_BASE_URL"))
        )

        resolved_api_key = (
            api_key or settings.resolved_llm_api_key or os.getenv("GAPGPT_API_KEY")
        )

        if client is not None:
            self._client = client
        elif resolved_api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(
                    api_key=resolved_api_key,
                    base_url=self._base_url or None,
                )
            except ImportError:
                self._client = None
                self._logger.error(
                    "LLMService: 'openai' package is missing. "
                    "Install it to use LLM generation."
                )
        else:
            self._client = None
            self._logger.warning(
                "LLMService: No API key provided (OPENAI_API_KEY or GAPGPT_API_KEY). "
                "Calls will fall back to raw context."
            )

    async def generate(
        self,
        query: str = "",
        context: list[RetrievalResult] | None = None,
        history: list[dict] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate answer for query based on retrieved context and conversation history.
        """
        actual_query = query or kwargs.get("question", "")
        raw_context = context if context is not None else kwargs.get("context", [])

        if not raw_context:
            return NO_RESULTS_FOUND

        formatted_context = _format_context(raw_context)
        if not formatted_context.strip():
            return NO_RESULTS_FOUND

        if self._client is None:
            self._logger.warning(
                "LLMService: Client not initialized (missing API key) — returning raw context"
            )
            return formatted_context

        system_prompt = SYSTEM_PROMPT.replace("{context}", formatted_context)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]
        if history:
            for turn in history:
                if isinstance(turn, dict) and "role" in turn and "content" in turn:
                    messages.append(
                        {"role": str(turn["role"]), "content": str(turn["content"])}
                    )
        messages.append({"role": "user", "content": actual_query})

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            raw = (response.choices[0].message.content or "").strip()
            return raw
        except Exception as exc:
            self._logger.error(
                "LLM generation failed",
                exc_info=True,
            )
            raise LLMError("LLM generation failed") from exc
