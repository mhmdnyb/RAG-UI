"""
Contract tests. Add your class to the matching list when your module is
ready; a violation of the interface fails here rather than on
integration day.
"""

import pytest

from app.common.fakes import (
    FakeEmbedding,
    FakeLLM,
    FakeReranker,
    FakeRetriever,
    FakeRouter,
)
from app.common.interfaces import RetrievalResult, RouteResult
from app.embedding.service import EmbeddingService
from app.llm.service import LLMService
from app.query_router.router import QueryRouter
from app.retrieval.reranker.reranker import Reranker
from app.retrieval.text_pipeline.retriever import TextRetriever
from tests.doubles import FakeCrossEncoder, FakeLlamaEmbedModel, FakeLlamaIndex

# SQLRetriever is omitted: importing it pulls in llama-index. Add it
# once that import is lazy.
RETRIEVERS = [FakeRetriever(), TextRetriever(index=FakeLlamaIndex())]
RERANKERS = [FakeReranker(), Reranker(model=FakeCrossEncoder())]
LLMS = [FakeLLM(), LLMService()]
EMBEDDERS = [FakeEmbedding(), EmbeddingService(model=FakeLlamaEmbedModel())]
ROUTERS = [FakeRouter(), QueryRouter()]


@pytest.mark.parametrize("retriever", RETRIEVERS)
async def test_retriever_returns_retrieval_results(retriever):
    results = await retriever.retrieve("سوال", top_k=3)
    assert isinstance(results, list)
    assert all(isinstance(r, RetrievalResult) for r in results)
    assert len(results) <= 3


@pytest.mark.parametrize("reranker", RERANKERS)
async def test_reranker_respects_top_k_and_returns_subset(reranker):
    items = [
        RetrievalResult(content=f"c{i}", source="d.pdf", page=i, score=i / 10)
        for i in range(5)
    ]
    ranked = await reranker.rerank("سوال", items, top_k=2)
    assert len(ranked) <= 2
    assert all(r in items for r in ranked)


@pytest.mark.parametrize("llm", LLMS)
async def test_llm_returns_non_empty_string(llm):
    items = [RetrievalResult(content="محتوا", source="d.pdf", page=1)]
    answer = await llm.generate("سوال", items)
    assert isinstance(answer, str)
    assert answer.strip()


@pytest.mark.parametrize("embedder", EMBEDDERS)
async def test_embedder_returns_one_vector_per_text(embedder):
    vectors = await embedder.embed(["a", "b"])
    assert len(vectors) == 2
    assert all(isinstance(v, list) for v in vectors)


@pytest.mark.parametrize("router", ROUTERS)
async def test_router_returns_route_result(router):
    result = await router.route("سوال نمونه")
    assert isinstance(result, RouteResult)
    assert result.route in ("sql", "text", "all")
