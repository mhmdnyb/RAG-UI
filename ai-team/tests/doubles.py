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
