import re

from app.models import Chunk, Document


class IngestionService:
    def chunk_document(self, document: Document, chunk_size: int = 700, overlap: int = 120) -> list[Chunk]:
        content = document.content.strip()
        if not content:
            return []
        if chunk_size <= 0:
            chunk_size = 700
        overlap = max(0, min(overlap, chunk_size - 1))
        semantic_units = self._semantic_units(content)
        # Fallback to deterministic sliding windows for texts without usable semantic boundaries.
        if len(semantic_units) <= 1:
            return self._sliding_chunks(document.id, content, chunk_size, overlap)
        chunks: list[Chunk] = []
        index = 0
        buffer = ""
        for unit in semantic_units:
            candidate = f"{buffer}\n\n{unit}".strip() if buffer else unit
            if len(candidate) <= chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunk_text = buffer.strip()
                if chunk_text:
                    chunks.append(Chunk(document_id=document.id, chunk_index=index, content=chunk_text))
                    index += 1
                overlap_tail = self._tail_with_overlap(buffer, overlap)
                if overlap_tail and overlap_tail != unit:
                    maybe_merged = f"{overlap_tail}\n\n{unit}".strip()
                    buffer = maybe_merged if len(maybe_merged) <= chunk_size else unit
                else:
                    buffer = unit
            else:
                # Unit itself exceeds chunk_size; emit sliding windows and keep only the
                # overlap tail so subsequent units are not prefixed with an oversized buffer.
                sub_chunks = self._sliding_chunks(document.id, unit, chunk_size, overlap)
                for sc in sub_chunks:
                    sc.chunk_index = index
                    chunks.append(sc)
                    index += 1
                buffer = self._tail_with_overlap(unit, overlap)
        if buffer.strip():
            chunks.append(Chunk(document_id=document.id, chunk_index=index, content=buffer.strip()))
        return chunks

    def _sliding_chunks(self, document_id: int, content: str, chunk_size: int, overlap: int) -> list[Chunk]:
        chunks: list[Chunk] = []
        start = 0
        index = 0
        while start < len(content):
            end = min(len(content), start + chunk_size)
            snippet = content[start:end].strip()
            if snippet:
                chunks.append(Chunk(document_id=document_id, chunk_index=index, content=snippet))
                index += 1
            if end >= len(content):
                break
            start = end - overlap
        return chunks

    def _semantic_units(self, content: str) -> list[str]:
        paragraphs = [segment.strip() for segment in re.split(r"\n{2,}", content) if segment.strip()]
        units: list[str] = []
        for paragraph in paragraphs:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            units.extend([sentence.strip() for sentence in sentences if sentence.strip()])
        return units or [content]

    def _tail_with_overlap(self, text: str, overlap: int) -> str:
        if overlap <= 0 or len(text) <= overlap:
            return text
        return text[-overlap:]
