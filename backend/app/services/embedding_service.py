import hashlib


class EmbeddingService:
    def __init__(self, dimensions: int = 32) -> None:
        self.dimensions = dimensions

    def embed_text(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [digest[i % len(digest)] / 255 for i in range(self.dimensions)]
        return values
