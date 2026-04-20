from dataclasses import dataclass

import numpy as np


@dataclass
class SearchResult:
    item_id: int
    score: float
    vector_score: float = 0.0
    keyword_score: float = 0.0
    rerank_score: float = 0.0


class VectorStore:
    def add(self, item_id: int, vector: list[float]) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def search(self, vector: list[float], top_k: int = 3) -> list[SearchResult]:  # pragma: no cover
        raise NotImplementedError


class FaissVectorStore(VectorStore):
    def __init__(self, dimensions: int = 32) -> None:
        self.dimensions = dimensions
        self.ids: list[int] = []
        self.matrix = np.empty((0, self.dimensions), dtype="float32")
        self._faiss = None
        self._index = None
        try:
            import faiss  # type: ignore

            self._faiss = faiss
            self._index = faiss.IndexFlatIP(self.dimensions)
        except Exception:
            self._faiss = None
            self._index = None

    def _normalize(self, vector: list[float]) -> np.ndarray:
        arr = np.array(vector, dtype="float32").reshape(1, -1)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return arr
        return arr / norm

    def add(self, item_id: int, vector: list[float]) -> None:
        normed = self._normalize(vector)
        self.ids.append(item_id)
        self.matrix = np.vstack([self.matrix, normed])
        if self._index is not None:
            self._index.add(normed)

    def search(self, vector: list[float], top_k: int = 3) -> list[SearchResult]:
        if not self.ids:
            return []
        query = self._normalize(vector)
        if self._index is not None:
            distances, indices = self._index.search(query, top_k)
            results: list[SearchResult] = []
            for score, idx in zip(distances[0], indices[0], strict=False):
                if idx < 0 or idx >= len(self.ids):
                    continue
                results.append(
                    SearchResult(
                        item_id=self.ids[idx],
                        score=float(score),
                        vector_score=float(score),
                    )
                )
            return results

        scores = (self.matrix @ query.T).reshape(-1)
        ranked = np.argsort(-scores)[:top_k]
        return [
            SearchResult(
                item_id=self.ids[int(idx)],
                score=float(scores[int(idx)]),
                vector_score=float(scores[int(idx)]),
            )
            for idx in ranked
        ]


vector_store = FaissVectorStore(dimensions=32)
