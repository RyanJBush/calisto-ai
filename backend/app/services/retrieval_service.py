from collections import Counter

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models import Chunk, Document
from app.services.embedding_service import EmbeddingService
from app.services.rerank_service import RerankService, RetrievalCandidate
from app.services.text_utils import tokenize
from app.services.vector_store import SearchResult, vector_store


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()
        self.rerank_service = RerankService()

    def retrieve(self, query: str, organization_id: int, top_k: int = 3) -> list[tuple[Chunk, SearchResult]]:
        query_vector = self.embedding_service.embed_text(query)
        vector_matches = vector_store.search(query_vector, top_k=max(top_k * 4, 8))
        keyword_scores = self._keyword_search(query, organization_id, limit=max(top_k * 8, 16))

        max_vector_score = max((match.score for match in vector_matches), default=1.0)
        combined: dict[int, RetrievalCandidate] = {}

        for match in vector_matches:
            chunk = (
                self.db.query(Chunk)
                .options(joinedload(Chunk.document))
                .join(Document, Chunk.document_id == Document.id)
                .filter(Chunk.id == match.item_id, Document.organization_id == organization_id)
                .first()
            )
            if chunk is None:
                continue
            normalized_vector_score = match.score / max_vector_score if max_vector_score > 0 else 0.0
            combined[chunk.id] = RetrievalCandidate(
                chunk=chunk,
                vector_score=normalized_vector_score,
                keyword_score=0.0,
                blended_score=normalized_vector_score * 0.65,
            )

        for chunk_id, keyword_score in keyword_scores.items():
            if chunk_id in combined:
                candidate = combined[chunk_id]
                candidate.keyword_score = keyword_score
                candidate.blended_score = (candidate.vector_score * 0.65) + (keyword_score * 0.35)
                continue

            chunk = (
                self.db.query(Chunk)
                .options(joinedload(Chunk.document))
                .join(Document, Chunk.document_id == Document.id)
                .filter(Chunk.id == chunk_id, Document.organization_id == organization_id)
                .first()
            )
            if chunk is None:
                continue

            combined[chunk.id] = RetrievalCandidate(
                chunk=chunk,
                vector_score=0.0,
                keyword_score=keyword_score,
                blended_score=keyword_score * 0.35,
            )

        reranked = self.rerank_service.rerank(query, list(combined.values()), top_k=top_k)
        results: list[tuple[Chunk, SearchResult]] = []
        for candidate in reranked:
            rerank_score = self.rerank_service.score(query, candidate)
            results.append(
                (
                    candidate.chunk,
                    SearchResult(
                        item_id=candidate.chunk.id,
                        score=rerank_score,
                        vector_score=candidate.vector_score,
                        keyword_score=candidate.keyword_score,
                        rerank_score=rerank_score,
                    ),
                )
            )
        return results

    def _keyword_search(self, query: str, organization_id: int, limit: int) -> dict[int, float]:
        query_terms = self._tokens(query)
        if not query_terms:
            return {}

        query_counter = Counter(query_terms)
        query_term_set = set(query_terms)
        content_filters = [Chunk.content.ilike(f"%{term}%") for term in query_term_set]
        candidates = (
            self.db.query(Chunk)
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.organization_id == organization_id, or_(*content_filters))
            .limit(max(limit * 5, 50))
            .all()
        )

        scored: list[tuple[int, float]] = []
        for chunk in candidates:
            chunk_terms = self._tokens(chunk.content)
            if not chunk_terms:
                continue
            chunk_counter = Counter(chunk_terms)
            shared_terms = query_term_set & set(chunk_terms)
            if not shared_terms:
                continue

            overlap = sum(min(query_counter[term], chunk_counter[term]) for term in shared_terms) / len(query_terms)
            density = len(shared_terms) / len(query_term_set)
            score = min(1.0, (overlap * 0.7) + (density * 0.3))
            scored.append((chunk.id, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return dict(scored[:limit])

    def _tokens(self, text: str) -> list[str]:
        return tokenize(text)
