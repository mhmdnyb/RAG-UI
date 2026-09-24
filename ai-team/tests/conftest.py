import os

# Never touch Redis, a real database or a real model.
os.environ.setdefault("USE_QUEUE", "false")
os.environ.setdefault("RAG_SERVICE_TOKEN", "test-token")
os.environ.setdefault("CORE_SERVICE_URL", "http://core.test")

import pytest

from app.common.fakes import FakeLLM, FakeReranker, FakeRetriever, FakeRouter
from app.orchestrator.pipeline import QueryOrchestrator


@pytest.fixture
def orchestrator() -> QueryOrchestrator:
    return QueryOrchestrator(
        retrievers={"text": FakeRetriever()},
        reranker=FakeReranker(),
        llm=FakeLLM(),
        router=FakeRouter("text"),
    )


@pytest.fixture
def client(orchestrator, monkeypatch):
    from fastapi.testclient import TestClient

    from app.server import create_app

    sent: list[dict] = []

    async def fake_send_callback(conversation_id, answer, sources=None, **kw):
        sent.append(
            {
                "conversationId": conversation_id,
                "answer": answer,
                "sources": sources,
            }
        )

    monkeypatch.setattr("app.worker.tasks.send_callback", fake_send_callback)

    with TestClient(create_app(orchestrator=orchestrator)) as c:
        c.sent_callbacks = sent
        yield c
