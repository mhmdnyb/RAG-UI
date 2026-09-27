"""Tests for LLM answer generation service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.constants import NO_RESULTS_FOUND
from app.common.exceptions import LLMError
from app.common.interfaces import RetrievalResult
from app.llm.service import LLMService


def _make_mock_client(return_content: str = "پاسخ تست"):
    client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = return_content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    client.chat.completions.create = AsyncMock(return_value=mock_response)
    return client


async def test_empty_context_returns_no_results_found():
    service = LLMService(api_key="")
    answer = await service.generate("سوال کاربر", [])
    assert answer == NO_RESULTS_FOUND


async def test_blank_content_returns_no_results_found():
    service = LLMService(api_key="")
    answer = await service.generate(
        "سوال کاربر",
        [RetrievalResult(content="   ", source="doc.pdf")],
    )
    assert answer == NO_RESULTS_FOUND


async def test_uninitialized_client_falls_back_to_formatted_context():
    service = LLMService(api_key="", client=None)
    items = [
        RetrievalResult(content="محتوای اول", source="doc1.pdf", page=2),
        RetrievalResult(content="محتوای دوم", source="doc2.pdf"),
    ]
    answer = await service.generate("سوال", items)
    assert "[doc1.pdf, صفحه 2]" in answer
    assert "محتوای اول" in answer
    assert "[doc2.pdf]" in answer
    assert "محتوای دوم" in answer


async def test_generation_happy_path_calls_client():
    mock_client = _make_mock_client("پاسخ مدل هوش مصنوعی")
    service = LLMService(
        model="test-model",
        temperature=0.2,
        max_tokens=500,
        client=mock_client,
    )
    items = [RetrievalResult(content="اطلاعات درس", source="rules.pdf", page=10)]
    answer = await service.generate("ساعت کلاس کی است؟", items)

    assert answer == "پاسخ مدل هوش مصنوعی"
    mock_client.chat.completions.create.assert_awaited_once()

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["temperature"] == 0.2
    assert call_kwargs["max_tokens"] == 500

    messages = call_kwargs["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "You are a university assistant." in messages[0]["content"]
    assert "[rules.pdf, صفحه 10]" in messages[0]["content"]
    assert "اطلاعات درس" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "ساعت کلاس کی است؟"


async def test_generation_includes_history():
    mock_client = _make_mock_client("پاسخ با تاریخچه")
    service = LLMService(client=mock_client)
    history = [
        {"role": "user", "content": "سلام"},
        {"role": "assistant", "content": "درود، در خدمتم."},
    ]
    items = [RetrievalResult(content="قوانین", source="reg.pdf")]
    await service.generate("سوال بعدی", items, history=history)

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    messages = call_kwargs["messages"]
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "سلام"}
    assert messages[2] == {"role": "assistant", "content": "درود، در خدمتم."}
    assert messages[3] == {"role": "user", "content": "سوال بعدی"}


async def test_generation_failure_raises_llm_error():
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("API Connection timeout")
    )
    service = LLMService(client=client)

    items = [RetrievalResult(content="قوانین", source="reg.pdf")]
    with pytest.raises(LLMError, match="LLM generation failed"):
        await service.generate("سوال", items)


async def test_supports_kwargs_and_string_context():
    mock_client = _make_mock_client("پاسخ سازگار")
    service = LLMService(client=mock_client)
    answer = await service.generate(
        question="سوال آزمایشی", context="متن کمکی به صورت رشته"
    )
    assert answer == "پاسخ سازگار"
