from collections import Counter
from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models import Chunk, Document
from app.services.embedding_service import EmbeddingService
from app.services.rerank_service import RerankService, RetrievalCandidate
from app.services.text_utils import tokenize
from app.services.vector_store import SearchResult, vector_store


@dataclass
class RetrievalFilters:
    source_name: str | None = None
    document_ids: list[int] | None = None
    collection_id: int | None = None


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()
        self.rerank_service = RerankService()

    def retrieve(
        self,
        query: str,
        organization_id: int,
        top_k: int = 3,
        filters: RetrievalFilters | None = None,
    ) -> list[tuple[Chunk, SearchResult]]:
        filters = filters or RetrievalFilters()
        query_vector = self.embedding_service.embed_text(query)
        vector_matches = vector_store.search(query_vector, top_k=max(top_k * 4, 8))
        keyword_scores = self._keyword_search(
            query,
            organization_id,
            limit=max(top_k * 8, 16),
            filters=filters,
        )

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
            if chunk is None or not self._matches_filters(chunk, filters):
                continue
            normalized_vector_score = match.score / max_vector_score if max_vector_score > 0 else 0.0
            metadata_score = self._metadata_score(chunk, query)
            combined[chunk.id] = RetrievalCandidate(
                chunk=chunk,
                vector_score=normalized_vector_score,
                keyword_score=0.0,
                metadata_score=metadata_score,
                blended_score=(normalized_vector_score * 0.60) + (metadata_score * 0.10),
            )

        for chunk_id, keyword_score in keyword_scores.items():
            if chunk_id in combined:
                candidate = combined[chunk_id]
                candidate.keyword_score = keyword_score
                candidate.blended_score = (
                    (candidate.vector_score * 0.60) + (keyword_score * 0.30) + (candidate.metadata_score * 0.10)
                )
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

            metadata_score = self._metadata_score(chunk, query)
            combined[chunk.id] = RetrievalCandidate(
                chunk=chunk,
                vector_score=0.0,
                keyword_score=keyword_score,
                metadata_score=metadata_score,
                blended_score=(keyword_score * 0.30) + (metadata_score * 0.10),
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

    def _keyword_search(
        self,
        query: str,
        organization_id: int,
        limit: int,
        filters: RetrievalFilters,
    ) -> dict[int, float]:
        query_terms = self._tokens(query)
        if not query_terms:
            return {}

        query_counter = Counter(query_terms)
        query_term_set = set(query_terms)
        content_filters = [Chunk.content.ilike(f"%{term}%") for term in query_term_set]
        title_filters = [Document.title.ilike(f"%{term}%") for term in query_term_set]
        source_filters = [Document.source_name.ilike(f"%{term}%") for term in query_term_set]
        combined_or_filters = content_filters + title_filters + source_filters
        if not combined_or_filters:
            return {}

        query_builder = (
            self.db.query(Chunk)
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.organization_id == organization_id, or_(*combined_or_filters))
        )
        if filters.source_name:
            query_builder = query_builder.filter(Document.source_name.ilike(f"%{filters.source_name}%"))
        if filters.document_ids:
            query_builder = query_builder.filter(Document.id.in_(filters.document_ids))
        if filters.collection_id:
            query_builder = query_builder.filter(Document.collection_id == filters.collection_id)

        candidates = (
            query_builder.options(joinedload(Chunk.document))
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

            overlap = sum(min(query_counter[term], chunk_counter[term]) for term in shared_terms) / max(
                1, len(query_terms)
            )
            density = len(shared_terms) / max(1, len(query_term_set))
            metadata_score = self._metadata_score(chunk, query)
            score = min(1.0, (overlap * 0.55) + (density * 0.25) + (metadata_score * 0.20))
            scored.append((chunk.id, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return dict(scored[:limit])

    def _tokens(self, text: str) -> list[str]:
        return tokenize(text)

    def _metadata_score(self, chunk: Chunk, query: str) -> float:
        query_terms = set(self._tokens(query))
        if not query_terms:
            return 0.0
        title_terms = set(self._tokens(chunk.document.title))
        source_terms = set(self._tokens(chunk.document.source_name))
        title_overlap = len(query_terms & title_terms) / max(1, len(query_terms))
        source_overlap = len(query_terms & source_terms) / max(1, len(query_terms))
        return min(1.0, (title_overlap * 0.7) + (source_overlap * 0.3))

    def _matches_filters(self, chunk: Chunk, filters: RetrievalFilters) -> bool:
        if filters.document_ids is not None and len(filters.document_ids) == 0:
            return False
        if filters.document_ids and chunk.document_id not in filters.document_ids:
            return False
        if filters.source_name and filters.source_name.lower() not in chunk.document.source_name.lower():
            return False
        if filters.collection_id and chunk.document.collection_id != filters.collection_id:
            return False
        return True
