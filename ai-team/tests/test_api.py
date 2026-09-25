"""API contract tests — these protect the agreement with Core Service."""

import time


def _wait_for(predicate, timeout: float = 5.0):
    """The job is queued, so the callback lands after the ACK."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    raise AssertionError("condition not met in time")


AUTH = {"Authorization": "Bearer test-token"}


def test_health_is_public(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_query_requires_token(client):
    r = client.post("/rag/query", json={"conversationId": "c1", "question": "س"})
    assert r.status_code == 401


def test_query_rejects_wrong_token(client):
    r = client.post(
        "/rag/query",
        json={"conversationId": "c1", "question": "س"},
        headers={"Authorization": "Bearer nope"},
    )
    assert r.status_code == 401


def test_query_acks_with_literal_ok(client):
    # Core does `"OK".equals(status)`; this string must never change.
    r = client.post(
        "/rag/query",
        json={"conversationId": "c1", "question": "کلاس آمار کی است؟"},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}


def test_query_rejects_empty_question(client):
    r = client.post(
        "/rag/query",
        json={"conversationId": "c1", "question": ""},
        headers=AUTH,
    )
    assert r.status_code == 422


def test_callback_is_always_sent(client):
    client.post(
        "/rag/query",
        json={"conversationId": "c42", "question": "سوال تست"},
        headers=AUTH,
    )
    _wait_for(lambda: client.sent_callbacks)
    assert len(client.sent_callbacks) == 1
    cb = client.sent_callbacks[0]
    assert cb["conversationId"] == "c42"
    assert cb["answer"]
    assert cb["sources"] == [{"document": "fake.pdf", "page": 1}]


def test_response_carries_request_id(client):
    r = client.get("/health")
    assert r.headers.get("x-request-id")


def test_query_rejects_whitespace_only_question(client):
    r = client.post(
        "/rag/query",
        json={"conversationId": "c1", "question": "   \n "},
        headers=AUTH,
    )
    assert r.status_code == 422


def test_query_rejects_oversized_question_instead_of_truncating(client):
    from app.common.config import settings

    r = client.post(
        "/rag/query",
        json={
            "conversationId": "c1",
            "question": "س" * (settings.max_question_length + 1),
        },
        headers=AUTH,
    )
    assert r.status_code == 422


def test_ready_returns_503_when_a_dependency_is_down(client, monkeypatch):
    monkeypatch.setattr("app.api.routes._check_database", lambda: "unreachable")
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "not_ready"


def test_failed_callback_does_not_rerun_the_pipeline(orchestrator, monkeypatch):
    from fastapi.testclient import TestClient

    from app.common.exceptions import CallbackError
    from app.server import create_app

    runs = 0
    original = orchestrator.process_query

    async def counting(*args, **kw):
        nonlocal runs
        runs += 1
        return await original(*args, **kw)

    attempts = 0

    async def failing_callback(*args, **kw):
        nonlocal attempts
        attempts += 1
        raise CallbackError("core is down")

    monkeypatch.setattr(orchestrator, "process_query", counting)
    monkeypatch.setattr("app.worker.tasks.send_callback", failing_callback)

    with TestClient(create_app(orchestrator=orchestrator)) as c:
        c.post(
            "/rag/query",
            json={"conversationId": "c1", "question": "سوال"},
            headers=AUTH,
        )
        _wait_for(lambda: attempts >= 1)
        time.sleep(0.3)  # give a wrongful retry time to show up

    assert runs == 1
    assert attempts == 1


def test_upload_regulations_requires_token(client):
    r = client.post(
        "/rag/regulations/upload",
        files={"file": ("test.txt", b"sample content", "text/plain")},
    )
    assert r.status_code == 401


def test_upload_regulations_empty_file_rejected(client):
    r = client.post(
        "/rag/regulations/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
        headers=AUTH,
    )
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


def test_upload_regulations_success(client, monkeypatch):
    from app.retrieval.text_pipeline.ingest import IngestionResult

    async def fake_ingest(text, clear_existing=True, embedder=None):
        return IngestionResult(
            parent_articles_count=3,
            child_chunks_count=10,
            cleared_existing=clear_existing,
        )

    monkeypatch.setattr(
        "app.retrieval.text_pipeline.ingest.ingest_regulations_text",
        fake_ingest,
    )

    r = client.post(
        "/rag/regulations/upload",
        files={"file": ("regulations.txt", b"sample regulations text", "text/plain")},
        headers=AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["filename"] == "regulations.txt"
    assert data["parent_articles_count"] == 3
    assert data["child_chunks_count"] == 10
    assert data["cleared_existing"] is True


def test_import_embedded_regulations_success(client, monkeypatch):
    from app.retrieval.text_pipeline.ingest import IngestionResult

    async def fake_import(parents, chunks, clear_existing=True):
        return IngestionResult(
            parent_articles_count=len(parents),
            child_chunks_count=len(chunks),
            cleared_existing=clear_existing,
        )

    monkeypatch.setattr(
        "app.retrieval.text_pipeline.ingest.import_precomputed_regulations",
        fake_import,
    )

    payload = {
        "version": "1.0",
        "embedding_model": "BAAI/bge-m3",
        "parent_articles": [
            {"id": "art_1", "section": "sec", "title": "m1", "full_text": "text"}
        ],
        "chunks": [
            {
                "id": "c_1",
                "text": "chunk text",
                "metadata": {"type": "base"},
                "embedding": [0.1] * 1024,
            }
        ],
        "clear_existing": True,
    }

    r = client.post(
        "/rag/regulations/import-embedded",
        json=payload,
        headers=AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["parent_articles_count"] == 1
    assert data["child_chunks_count"] == 1


def test_import_embedded_regulations_file_success(client, monkeypatch):
    import json

    from app.retrieval.text_pipeline.ingest import IngestionResult

    async def fake_import(parents, chunks, clear_existing=True):
        return IngestionResult(
            parent_articles_count=len(parents),
            child_chunks_count=len(chunks),
            cleared_existing=clear_existing,
        )

    monkeypatch.setattr(
        "app.retrieval.text_pipeline.ingest.import_precomputed_regulations",
        fake_import,
    )

    payload = {
        "version": "1.0",
        "embedding_model": "BAAI/bge-m3",
        "parent_articles": [
            {"id": "art_1", "section": "sec", "title": "m1", "full_text": "text"}
        ],
        "chunks": [
            {
                "id": "c_1",
                "text": "chunk text",
                "metadata": {"type": "base"},
                "embedding": [0.1] * 1024,
            }
        ],
    }

    content = json.dumps(payload).encode("utf-8")
    r = client.post(
        "/rag/regulations/import-embedded-file",
        files={"file": ("embedded.json", content, "application/json")},
        headers=AUTH,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["parent_articles_count"] == 1
    assert data["child_chunks_count"] == 1
