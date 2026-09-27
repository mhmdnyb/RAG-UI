"""
Routes a question to the SQL pipeline, the text pipeline, or both.

Uses an LLM call (via OpenRouter or OpenAI) with JSON output format.
"""

from __future__ import annotations

import json
from logging import Logger
from typing import Any

from app.common.config import settings
from app.common.interfaces import BaseQueryRouter, RouteResult
from app.common.logger import get_logger

SYSTEM_PROMPT = """تو یک متخصص تشخیص نوع پرسش برای یک سیستم RAG هستی.
باید تشخیص بدی سوال کاربر به کدام دو حالت زیر مربوطه :

1) sql — وقتی سوال درباره‌ی جدول کلاس ها و زمانبندی و اساتید است.
جدول کلاس‌های دانشگاه با ستون‌های: درس، ساعت، استاد، روز.
نمونه ردیف: شبیه سازی کامپیوتر | 10-12 | زهرا شیرین کام | یکشنبه

2) text — وقتی سوال درباره‌ی مقررات آموزشی دانشگاه است.

فقط و فقط یک JSON با فرمت زیر خروجی بده:
{"route": "sql"} یا {"route": "text"}

سوال: کلاس شبکه کامپیوتری کی برگزار می‌شه؟ -> sql
سوال: استاد کلاس یکشنبه ساعت ۱۰ کیه؟ -> sql
سوال: چه درس‌هایی روز سه‌شنبه هست؟ -> sql
سوال: مدت مجاز تحصیل در دوره کارشناسی ارشد چقدر است ؟ -> text
سوال: حداکثر غیبت مجاز برای هر درس چقدر است ؟ -> text"""


class QueryRouter(BaseQueryRouter):
    """
    LLM-based classifier determining whether a query targets SQL or Text.

    Supports custom model, temperature, base_url, or injected client.
    Defaults to settings.router_* configuration.
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        client: Any | None = None,
        logger: Logger | None = None,
    ):
        self._logger = logger or get_logger(__name__)
        self._model = model or settings.resolved_router_model
        self._temperature = (
            temperature if temperature is not None else settings.router_temperature
        )
        self._base_url = (
            base_url if base_url is not None else settings.resolved_router_base_url
        )

        resolved_api_key = api_key or settings.resolved_router_api_key

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
                    "QueryRouter: 'openai' package is missing. "
                    "Install it to use LLM routing. Falling back to safe mode."
                )
        else:
            self._client = None
            self._logger.warning(
                "QueryRouter: No API key provided (ROUTER_API_KEY or OPENAI_API_KEY). "
                "Calls will use safe fallback ('text')."
            )

    async def route(self, query: str) -> RouteResult:
        """Classify query using LLM and return RouteResult."""
        if self._client is None:
            self._logger.warning(
                "QueryRouter: Client not initialized (missing API key); falling back to 'text'"
            )
            return RouteResult(route="text", question=query, confidence=0.0)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                temperature=self._temperature,
                # برای مدل‌هایی مثل OpenAI می‌توانید خط زیر را از کامنت خارج کنید:
                # response_format={"type": "json_object"},
            )
            raw = (response.choices[0].message.content or "").strip()

            route = ""
            try:
                parsed = json.loads(raw)
                route = str(parsed.get("route", "")).strip().lower()
            except Exception:
                import re

                match = re.search(r'"route"\s*:\s*"(sql|text)"', raw, re.IGNORECASE)
                if match:
                    route = match.group(1).lower()

            if route in ("sql", "text"):
                self._logger.info(f"Query routed to '{route}': {query[:50]}")
                return RouteResult(route=route, question=query, confidence=1.0)

            self._logger.warning(
                f"QueryRouter: Invalid route value in response ({raw!r}); falling back to 'text'"
            )
        except Exception as e:
            self._logger.warning(
                f"QueryRouter: LLM routing failed ({e}); falling back to 'text'",
                exc_info=True,
            )

        # Fallback امن: اگر مدل خروجی نامعتبر داد، پیش‌فرض را text بگذار
        return RouteResult(route="text", question=query, confidence=0.5)
