from hashlib import sha256

from app.core.config import settings


class EmbeddingService:
    """Deterministic embedding placeholder; swap with provider implementation later."""

    def __init__(self, dimensions: int | None = None) -> None:
        self.dimensions = dimensions or settings.embedding_dimension

    def embed_text(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.dimensions

        vector = [0.0] * self.dimensions
        words = text.lower().split()
        for word in words:
            digest = sha256(word.encode("utf-8")).digest()
            for idx in range(self.dimensions):
                vector[idx] += digest[idx] / 255.0

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]
