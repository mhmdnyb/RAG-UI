"""Tests for the LLM-based QueryRouter."""

from unittest.mock import AsyncMock, MagicMock

from app.common.interfaces import RouteResult
from app.query_router.router import QueryRouter


def _make_mock_client(content: str) -> MagicMock:
    """Helper to build a mock AsyncOpenAI client returning a specific string."""
    choice = MagicMock()
    choice.message.content = content

    response = MagicMock()
    response.choices = [choice]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


async def test_query_router_routes_sql():
    mock_client = _make_mock_client('{"route": "sql"}')
    router = QueryRouter(client=mock_client)

    result = await router.route("کلاس شبکه کامپیوتری کی برگزار می‌شه؟")

    assert isinstance(result, RouteResult)
    assert result.route == "sql"
    assert result.confidence == 1.0
    assert result.question == "کلاس شبکه کامپیوتری کی برگزار می‌شه؟"

    mock_client.chat.completions.create.assert_awaited_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert (
        call_kwargs["messages"][1]["content"] == "کلاس شبکه کامپیوتری کی برگزار می‌شه؟"
    )


async def test_query_router_routes_markdown_json():
    mock_client = _make_mock_client('```json\n{"route": "sql"}\n```')
    router = QueryRouter(client=mock_client)

    result = await router.route("کلاس پایگاه داده کی هست؟")

    assert isinstance(result, RouteResult)
    assert result.route == "sql"
    assert result.confidence == 1.0


async def test_query_router_routes_text():
    mock_client = _make_mock_client('{"route": "text"}')
    router = QueryRouter(client=mock_client)

    result = await router.route("مدت مجاز تحصیل در دوره کارشناسی ارشد چقدر است؟")

    assert isinstance(result, RouteResult)
    assert result.route == "text"
    assert result.confidence == 1.0


async def test_query_router_fallback_on_invalid_json():
    mock_client = _make_mock_client("not-a-json")
    router = QueryRouter(client=mock_client)

    result = await router.route("سوال مبهم")

    assert isinstance(result, RouteResult)
    assert result.route == "text"
    assert result.confidence == 0.5


async def test_query_router_fallback_on_unexpected_route_value():
    mock_client = _make_mock_client('{"route": "unknown_destination"}')
    router = QueryRouter(client=mock_client)

    result = await router.route("سوال نامربوط")

    assert isinstance(result, RouteResult)
    assert result.route == "text"
    assert result.confidence == 0.5


async def test_query_router_fallback_on_api_exception():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("API down")
    )
    router = QueryRouter(client=mock_client)

    result = await router.route("سوال هنگام خطای شبکه")

    assert isinstance(result, RouteResult)
    assert result.route == "text"
    assert result.confidence == 0.5


async def test_query_router_fallback_when_no_api_key():
    # Router without client or api_key
    router = QueryRouter(api_key="", client=None)
    # Ensure client is None
    router._client = None

    result = await router.route("سوال بدون کلید API")

    assert isinstance(result, RouteResult)
    assert result.route == "text"
    assert result.confidence == 0.0


def test_query_router_custom_model_and_temperature():
    router = QueryRouter(
        model="custom-meta-llama",
        temperature=0.3,
        base_url="https://custom.endpoint/v1",
        api_key="fake-key",
    )

    assert router._model == "custom-meta-llama"
    assert router._temperature == 0.3
    assert router._base_url == "https://custom.endpoint/v1"
