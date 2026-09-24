"""
Shared contracts between modules.

Every module implements one of these. Breaking a signature here breaks
everyone, so changes need team-wide review.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    content: str
    source: str  # document name, or "sql_query" for DB results
    page: int | None = None
    score: float = 0.0  # higher is more relevant
    metadata: dict = field(default_factory=dict)


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Return at most `top_k` results, most relevant first."""
        ...


class BaseReranker(ABC):
    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        """Re-score and return at most `top_k` of the given results."""
        ...


class BaseLLMService(ABC):
    @abstractmethod
    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        history: list[dict] | None = None,
    ) -> str: ...


class BaseEmbeddingService(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed documents. One vector per input, same order."""
        ...

    async def embed_query(self, text: str) -> list[float]:
        """
        Embed a search query.

        Separate from `embed` because asymmetric models (e5, bge) need a
        different prefix for queries than for documents.
        """
        vectors = await self.embed([text])
        return vectors[0]


class BaseChatHistory(ABC):
    @abstractmethod
    async def get_history(self, conversation_id: str) -> list[dict]:
        """Return [{"role": "user"|"assistant", "content": str}, ...]."""
        ...

    @abstractmethod
    async def save_turn(
        self, conversation_id: str, question: str, answer: str
    ) -> None: ...


@dataclass
class RouteResult:
    route: str  # "sql", "text" or "all"
    question: str
    confidence: float = 1.0


class BaseQueryRouter(ABC):
    @abstractmethod
    async def route(self, query: str) -> RouteResult:
        """Decide which retrieval pipeline should answer this question."""
        ...
