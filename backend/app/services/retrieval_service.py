from sqlalchemy.orm import Session

from app.models import Chunk
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import SearchResult, vector_store


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[Chunk, SearchResult]]:
        query_vector = self.embedding_service.embed_text(query)
        matches = vector_store.search(query_vector, top_k=top_k)
        results: list[tuple[Chunk, SearchResult]] = []
        for match in matches:
            chunk = self.db.get(Chunk, match.item_id)
            if chunk:
                results.append((chunk, match))
        return results
