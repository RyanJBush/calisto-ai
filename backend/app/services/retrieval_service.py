from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService


@dataclass
class RetrievalResult:
    chunk: DocumentChunk
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def retrieve_top_chunks(db: Session, organization_id: int, query: str, top_k: int) -> list[RetrievalResult]:
    embedder = EmbeddingService()
    query_embedding = embedder.embed_text(query)

    chunks = db.query(DocumentChunk).filter(DocumentChunk.organization_id == organization_id).all()
    scored = [
        RetrievalResult(chunk=chunk, score=cosine_similarity(query_embedding, chunk.embedding))
        for chunk in chunks
    ]
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]
