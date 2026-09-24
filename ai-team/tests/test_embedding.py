"""
Embedding adapter wiring: lazy loading, thread offloading, and the
query/document split. The model itself is not under test.
"""

import asyncio

from app.embedding.service import EmbeddingService
from tests.doubles import FakeLlamaEmbedModel


async def test_embed_documents_uses_batch_api():
    model = FakeLlamaEmbedModel()
    service = EmbeddingService(model=model)
    vectors = await service.embed(["الف", "ب"])
    assert len(vectors) == 2
    assert model.document_calls == [["الف", "ب"]]


async def test_embed_query_uses_query_api():
    model = FakeLlamaEmbedModel()
    service = EmbeddingService(model=model)
    await service.embed_query("سوال")
    assert model.query_calls == ["سوال"]
    assert model.document_calls == []  # must NOT go through the doc path


async def test_empty_input_short_circuits():
    model = FakeLlamaEmbedModel()
    assert await EmbeddingService(model=model).embed([]) == []
    assert model.document_calls == []


async def test_model_is_built_only_once():
    calls = []

    class Service(EmbeddingService):
        def _build_model(self):
            calls.append(1)
            return FakeLlamaEmbedModel()

    service = Service()
    await asyncio.gather(*(service.embed_query("س") for _ in range(5)))
    assert len(calls) == 1


async def test_inference_does_not_block_the_event_loop():
    """A slow model must not stop other coroutines from running."""
    import time

    class SlowModel(FakeLlamaEmbedModel):
        def get_query_embedding(self, text):
            time.sleep(0.2)  # blocking, as a real model is
            return super().get_query_embedding(text)

    service = EmbeddingService(model=SlowModel())
    ticks = 0

    async def ticker():
        nonlocal ticks
        while True:
            await asyncio.sleep(0.01)
            ticks += 1

    task = asyncio.create_task(ticker())
    await service.embed_query("سوال")
    task.cancel()
    assert ticks > 3, "event loop was blocked during inference"


async def test_warm_up_failure_is_raised_not_swallowed():
    import pytest

    from app.common.exceptions import EmbeddingError

    class BrokenModel(FakeLlamaEmbedModel):
        def get_query_embedding(self, text):
            raise RuntimeError("weights missing")

    with pytest.raises(EmbeddingError):
        await EmbeddingService(model=BrokenModel()).warm_up()
