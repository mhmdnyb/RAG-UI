"""Callback delivery: retry on 5xx, give up on 4xx."""

import httpx
import pytest

from app.api.callback import send_callback
from app.common.exceptions import CallbackError


class _Client:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0

    async def post(self, url, json=None, headers=None):
        self.calls += 1
        status = self.statuses.pop(0)
        response = httpx.Response(status, request=httpx.Request("POST", url), json={})
        return response


async def test_succeeds_first_try():
    client = _Client([200])
    await send_callback("c1", "پاسخ", [], client=client)
    assert client.calls == 1


async def test_retries_on_server_error(monkeypatch):
    monkeypatch.setattr("asyncio.sleep", _no_sleep)
    client = _Client([503, 200])
    await send_callback("c1", "پاسخ", [], client=client)
    assert client.calls == 2


async def test_does_not_retry_on_client_error(monkeypatch):
    monkeypatch.setattr("asyncio.sleep", _no_sleep)
    client = _Client([401, 200])
    with pytest.raises(CallbackError):
        await send_callback("c1", "پاسخ", [], client=client)
    assert client.calls == 1


async def _no_sleep(_seconds):
    return None
