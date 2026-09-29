"""Stand-ins for third-party objects we do not want to load in CI."""


class FakeLlamaEmbedModel:
    """Only the two methods EmbeddingService actually calls."""

    def __init__(self, dim: int = 4):
        self.dim = dim
        self.document_calls: list[list[str]] = []
        self.query_calls: list[str] = []

    def get_text_embedding_batch(self, texts, show_progress=False):
        self.document_calls.append(list(texts))
        return [[float(len(t))] * self.dim for t in texts]

    def get_query_embedding(self, text):
        self.query_calls.append(text)
        return [1.0] * self.dim


class FakeLlamaIndex:
    """Stand-in for VectorStoreIndex so TextRetriever contract test does not require a database."""

    def __init__(self, items=None):
        from unittest.mock import MagicMock

        if items is None:
            node = MagicMock()
            node.get_content.return_value = "متن نمونه"
            node.metadata = {"title": "آیین‌نامه نمونه"}
            item = MagicMock()
            item.node = node
            item.score = 0.9
            self._items = [item]
        else:
            self._items = items

    def as_retriever(self, similarity_top_k: int = 5):
        from unittest.mock import AsyncMock, MagicMock

        mock = MagicMock()
        mock.aretrieve = AsyncMock(return_value=self._items[:similarity_top_k])
        return mock


class FakeCrossEncoder:
    """Stand-in for CrossEncoder so Reranker contract test does not download models in CI."""

    def predict(self, pairs, **kwargs):
        return [float(len(p[1])) for p in pairs]


class FakeAsyncOpenAI:
    """Stand-in for AsyncOpenAI so LLM and Router contract tests do not hit network."""

    def __init__(self, response_text: str = "پاسخ مدل"):
        from unittest.mock import AsyncMock, MagicMock

        self.chat = MagicMock()
        choice = MagicMock()
        choice.message.content = response_text
        mock_resp = MagicMock()
        mock_resp.choices = [choice]
        self.chat.completions.create = AsyncMock(return_value=mock_resp)
