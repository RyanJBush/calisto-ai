import re
from dataclasses import dataclass

from app.models import Chunk

TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")


@dataclass
class RetrievalCandidate:
    chunk: Chunk
    vector_score: float
    keyword_score: float
    blended_score: float


class RerankService:
    def rerank(self, query: str, candidates: list[RetrievalCandidate], top_k: int) -> list[RetrievalCandidate]:
        query_terms = self._tokens(query)
        if not query_terms:
            return sorted(candidates, key=lambda candidate: candidate.blended_score, reverse=True)[:top_k]

        ranked: list[tuple[float, RetrievalCandidate]] = []
        for candidate in candidates:
            content_terms = set(self._tokens(candidate.chunk.content))
            title_terms = set(self._tokens(candidate.chunk.document.title))
            query_term_set = set(query_terms)

            coverage = len(content_terms & query_term_set) / len(query_term_set)
            title_boost = len(title_terms & query_term_set) / len(query_term_set)
            rerank_score = (candidate.blended_score * 0.55) + (coverage * 0.35) + (title_boost * 0.10)
            ranked.append((rerank_score, candidate))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [candidate for _score, candidate in ranked[:top_k]]

    def score(self, query: str, candidate: RetrievalCandidate) -> float:
        query_terms = set(self._tokens(query))
        if not query_terms:
            return candidate.blended_score

        content_terms = set(self._tokens(candidate.chunk.content))
        title_terms = set(self._tokens(candidate.chunk.document.title))
        coverage = len(content_terms & query_terms) / len(query_terms)
        title_boost = len(title_terms & query_terms) / len(query_terms)
        return (candidate.blended_score * 0.55) + (coverage * 0.35) + (title_boost * 0.10)

    def _tokens(self, text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())
