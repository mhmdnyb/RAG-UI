"""
Shared abstract interfaces (contracts) for all AI-team modules.

This file is the "constitution" of the project.
Every module implements one of these interfaces.
Changes to this file MUST be reviewed by all team members.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    """
    Standard data structure returned by all retrievers and consumed by
    the reranker, LLM service, and API layer.
    """
    content: str
    source: str              # document name, or "sql_query" for DB results
    page: int | None = None  # page number (None for non-document sources)
    score: float = 0.0       # relevance score (higher = more relevant)
    metadata: dict = field(default_factory=dict)


class BaseRetriever(ABC):
    """
    Contract for retrieval modules (SQL pipeline, text/vector pipeline, etc.).

    Owner: Dev 1 (SQL), Dev 2 (Text)
    """

    @abstractmethod
    async def retrieve(
        self, query: str, top_k: int = 5
    ) -> list[RetrievalResult]:
        """
        Given a user query, return a ranked list of retrieval results.
        """
        ...


class BaseReranker(ABC):
    """
    Contract for the reranking module.

    Owner: Dev 3
    """

    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        """
        Re-score and re-order a list of retrieval results.
        Return the top_k most relevant results.
        """
        ...


class BaseLLMService(ABC):
    """
    Contract for the LLM interaction module.

    Owner: Dev 4
    """

    @abstractmethod
    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        history: list[dict] | None = None,
    ) -> str:
        """
        Generate a natural-language answer given the user query,
        retrieved context, and optional conversation history.
        """
        ...


class BaseEmbeddingService(ABC):
    """
    Contract for the embedding module.

    Owner: Dev 5
    """

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of text strings into embedding vectors.
        """
        ...


class BaseChatHistory(ABC):
    """
    Contract for the chat history / conversation memory module.

    Owner: Dev 6
    """

    @abstractmethod
    async def get_history(self, conversation_id: str) -> list[dict]:
        """
        Retrieve the conversation history for a given conversation ID.
        Returns a list of {"role": "user"|"assistant", "content": "..."}.
        """
        ...

    @abstractmethod
    async def save_turn(
        self, conversation_id: str, question: str, answer: str
    ) -> None:
        """
        Persist a question-answer turn in the conversation history.
        """
        ...


@dataclass
class RouteResult:
    """
    Standard data structure returned by the query router.
    Specifies which retrieval pipeline(s) should process the question.
    """
    route: str               # "sql", "text", or "all"
    question: str            # Original user question
    confidence: float = 1.0  # Confidence score (optional, 0.0 - 1.0)


class BaseQueryRouter(ABC):
    """
    Contract for the query routing module.
    Classifies user questions to route them to the appropriate retrieval pipeline
    (SQL, Text/Vector, or all).

    Owner: Query Router Developer
    """

    @abstractmethod
    async def route(self, query: str) -> RouteResult:
        """
        Analyze the query and determine the target retrieval strategy.
        """
        ...
