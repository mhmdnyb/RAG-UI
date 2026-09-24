"""
Fake implementations of every interface.

Use them to run the pipeline without waiting for other modules:

    orchestrator = QueryOrchestrator(
        retrievers={"text": FakeRetriever()},
        reranker=FakeReranker(),
        llm=FakeLLM(),
    )
"""

from app.common.interfaces import (
    BaseEmbeddingService,
    BaseLLMService,
    BaseQueryRouter,
    BaseReranker,
    BaseRetriever,
    RetrievalResult,
    RouteResult,
)


class FakeRetriever(BaseRetriever):
    def __init__(self, results: list[RetrievalResult] | None = None):
        self._results = (
            results
            if results is not None
            else [
                RetrievalResult(
                    content="محتوای نمونه برای تست",
                    source="fake.pdf",
                    page=1,
                    score=0.9,
                )
            ]
        )

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        return self._results[:top_k]


class FailingRetriever(BaseRetriever):
    """Proves the pipeline survives a broken retriever."""

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        raise RuntimeError("boom")


class FakeReranker(BaseReranker):
    async def rerank(self, query, results, top_k: int = 3):
        return sorted(results, key=lambda r: r.score, reverse=True)[:top_k]


class FakeLLM(BaseLLMService):
    async def generate(self, query, context, history=None) -> str:
        return f"پاسخ نمونه به «{query}» بر اساس {len(context)} منبع."


class FakeEmbedding(BaseEmbeddingService):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)), 0.0, 1.0] for t in texts]


class FakeRouter(BaseQueryRouter):
    def __init__(self, route: str = "all"):
        self._route = route

    async def route(self, query: str) -> RouteResult:
        return RouteResult(route=self._route, question=query)
