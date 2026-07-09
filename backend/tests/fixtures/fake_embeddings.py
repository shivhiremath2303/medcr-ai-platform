from langchain_core.embeddings import Embeddings


class FakeEmbeddings(Embeddings):
    """
    Deterministic embedding model for testing.
    """

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(
        text: str,
    ) -> list[float]:
        length = float(len(text))
        checksum = float(sum(ord(char) for char in text) % 1000)

        return [
            length,
            checksum,
            length + checksum,
        ]


class FakeEmbeddingService:
    """
    Fake embedding service used by unit tests.
    """

    def __init__(self):
        self.model = FakeEmbeddings()
