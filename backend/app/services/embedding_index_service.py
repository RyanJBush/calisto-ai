import json
import math

from sqlalchemy.orm import Session

from app.models import Chunk, ChunkEmbedding, Document


class EmbeddingIndexService:
    def upsert_chunk_embedding(self, db: Session, chunk_id: int, vector: list[float]) -> None:
        existing = db.query(ChunkEmbedding).filter(ChunkEmbedding.chunk_id == chunk_id).first()
        payload = json.dumps(vector)
        if existing is None:
            db.add(ChunkEmbedding(chunk_id=chunk_id, dimensions=len(vector), vector=payload))
        else:
            existing.dimensions = len(vector)
            existing.vector = payload

    def delete_embeddings_for_chunk_ids(self, db: Session, chunk_ids: list[int]) -> None:
        if not chunk_ids:
            return
        db.query(ChunkEmbedding).filter(ChunkEmbedding.chunk_id.in_(chunk_ids)).delete(synchronize_session=False)

    def search(
        self,
        db: Session,
        query_vector: list[float],
        organization_id: int,
        filters,
        top_k: int,
    ) -> list[tuple[int, float]]:
        rows = (
            db.query(ChunkEmbedding.chunk_id, ChunkEmbedding.vector)
            .join(Chunk, ChunkEmbedding.chunk_id == Chunk.id)
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.organization_id == organization_id)
        )

        if filters.source_name:
            rows = rows.filter(Document.source_name.ilike(f"%{filters.source_name}%"))
        if filters.document_ids is not None and len(filters.document_ids) == 0:
            return []
        if filters.document_ids:
            rows = rows.filter(Document.id.in_(filters.document_ids))
        if filters.collection_id:
            rows = rows.filter(Document.collection_id == filters.collection_id)

        scored: list[tuple[int, float]] = []
        for chunk_id, serialized_vector in rows.all():
            candidate_vector = json.loads(serialized_vector)
            scored.append((int(chunk_id), self._cosine_similarity(query_vector, candidate_vector)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0

        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)


embedding_index_service = EmbeddingIndexService()
