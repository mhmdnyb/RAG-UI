"""Orchestrator behaviour, especially how it degrades under failure."""

import pytest

from app.common.constants import NO_RESULTS_FOUND
from app.common.exceptions import RetrievalError
from app.common.fakes import (
    FailingRetriever,
    FakeLLM,
    FakeReranker,
    FakeRetriever,
    FakeRouter,
)
from app.common.interfaces import RetrievalResult
from app.orchestrator.pipeline import QueryOrchestrator, _fuse


def _build(**kw) -> QueryOrchestrator:
    kw.setdefault("retrievers", {"text": FakeRetriever()})
    kw.setdefault("reranker", FakeReranker())
    kw.setdefault("llm", FakeLLM())
    return QueryOrchestrator(**kw)


async def test_happy_path_returns_answer_and_sources():
    answer, sources = await _build().process_query("c1", "سوال")
    assert answer
    assert sources == [{"document": "fake.pdf", "page": 1}]


async def test_one_broken_retriever_does_not_break_the_pipeline():
    orch = _build(retrievers={"sql": FailingRetriever(), "text": FakeRetriever()})
    answer, sources = await orch.process_query("c1", "سوال")
    assert sources  # the healthy retriever still contributed


async def test_no_results_returns_friendly_message():
    orch = _build(retrievers={"text": FakeRetriever(results=[])})
    answer, sources = await orch.process_query("c1", "سوال")
    assert answer == NO_RESULTS_FOUND
    assert sources == []


async def test_router_narrows_to_a_single_pipeline():
    sql_only = FakeRetriever(
        [RetrievalResult(content="rows", source="sql_query", score=1.0)]
    )
    orch = _build(
        retrievers={"sql": sql_only, "text": FakeRetriever()},
        router=FakeRouter("sql"),
    )
    _, sources = await orch.process_query("c1", "سوال")
    assert [s["document"] for s in sources] == ["sql_query"]


async def test_unknown_route_falls_back_to_all_retrievers():
    orch = _build(
        retrievers={"sql": FakeRetriever(), "text": FakeRetriever()},
        router=FakeRouter("something-else"),
    )
    _, sources = await orch.process_query("c1", "سوال")
    assert len(sources) >= 1


async def test_all_retrievers_failing_is_an_error_not_no_results():
    orch = _build(retrievers={"sql": FailingRetriever(), "text": FailingRetriever()})
    with pytest.raises(RetrievalError):
        await orch.process_query("c1", "سوال")


async def test_empty_plus_failed_is_an_error_not_no_results():
    orch = _build(
        retrievers={"sql": FailingRetriever(), "text": FakeRetriever(results=[])}
    )
    with pytest.raises(RetrievalError):
        await orch.process_query("c1", "سوال")


def _hits(source: str, *scores: float) -> list[RetrievalResult]:
    return [
        RetrievalResult(content=f"{source}-{i}", source=source, score=s)
        for i, s in enumerate(scores)
    ]


async def test_reranker_failure_falls_back_to_fused_order():
    class BrokenReranker(FakeReranker):
        async def rerank(self, query, results, top_k: int = 3):
            raise RuntimeError("boom")

    # "a" is registered first and has higher raw scores; fusion must still
    # interleave by rank instead of letting "a" take every slot.
    orch = _build(
        retrievers={
            "a": FakeRetriever(_hits("a", 90, 80, 70)),
            "b": FakeRetriever(_hits("b", 0.3, 0.2, 0.1)),
        },
        reranker=BrokenReranker(),
    )
    _, sources = await orch.process_query("c1", "سوال")
    assert {s["document"] for s in sources[:2]} == {"a", "b"}


def test_fusion_deduplicates_identical_chunks():
    same = RetrievalResult(content="x", source="doc.pdf", score=1.0, page=2)
    fused = _fuse([[same], [same]])
    assert len(fused) == 1
