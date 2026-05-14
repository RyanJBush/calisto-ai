from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session, joinedload

from app.models import Chunk, Document
from app.services.embedding_index_service import embedding_index_service
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalFilters
from app.services.text_utils import tokenize


@dataclass
class HybridSearchResult:
    chunk: Chunk
    score: float
    semantic_score: float
    bm25_score: float


class HybridSearchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    def search(
        self,
        query: str,
        organization_id: int,
        top_k: int = 8,
        filters: RetrievalFilters | None = None,
        rrf_k: int = 60,
    ) -> list[HybridSearchResult]:
        filters = filters or RetrievalFilters()
        chunks = self._fetch_candidate_chunks(organization_id, filters)
        if not chunks:
            return []

        query_vector = self.embedding_service.embed_text(query)
        vector_rank = embedding_index_service.search(
            db=self.db,
            query_vector=query_vector,
            organization_id=organization_id,
            filters=filters,
            top_k=max(top_k * 6, 30),
        )
        semantic_scores = {chunk_id: score for chunk_id, score in vector_rank}

        tokenized_corpus = [tokenize(chunk.content) for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores_raw = bm25.get_scores(tokenize(query))
        bm25_scores = {chunk.id: float(score) for chunk, score in zip(chunks, bm25_scores_raw, strict=False)}

        semantic_sorted = [chunk_id for chunk_id, _ in sorted(semantic_scores.items(), key=lambda x: x[1], reverse=True)]
        bm25_sorted = [chunk_id for chunk_id, _ in sorted(bm25_scores.items(), key=lambda x: x[1], reverse=True)]

        semantic_rank = {chunk_id: idx + 1 for idx, chunk_id in enumerate(semantic_sorted)}
        bm25_rank = {chunk_id: idx + 1 for idx, chunk_id in enumerate(bm25_sorted)}

        by_id = {chunk.id: chunk for chunk in chunks}
        fused: list[HybridSearchResult] = []
        for chunk_id in by_id:
            s_rank = semantic_rank.get(chunk_id)
            b_rank = bm25_rank.get(chunk_id)
            rrf_score = (1 / (rrf_k + s_rank) if s_rank else 0.0) + (1 / (rrf_k + b_rank) if b_rank else 0.0)
            fused.append(
                HybridSearchResult(
                    chunk=by_id[chunk_id],
                    score=rrf_score,
                    semantic_score=float(semantic_scores.get(chunk_id, 0.0)),
                    bm25_score=float(bm25_scores.get(chunk_id, 0.0)),
                )
            )

        fused.sort(key=lambda item: item.score, reverse=True)
        return fused[:top_k]

    def _fetch_candidate_chunks(self, organization_id: int, filters: RetrievalFilters) -> list[Chunk]:
        query = self.db.query(Chunk).join(Document, Chunk.document_id == Document.id).options(joinedload(Chunk.document))
        query = query.filter(Document.organization_id == organization_id)
        if filters.document_ids:
            query = query.filter(Document.id.in_(filters.document_ids))
        if filters.collection_id:
            query = query.filter(Document.collection_id == filters.collection_id)
        if filters.source_name:
            query = query.filter(Document.source_name.ilike(f"%{filters.source_name}%"))
        return query.limit(1000).all()
