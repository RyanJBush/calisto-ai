from app.models import Chunk, Document


class IngestionService:
    def chunk_document(self, document: Document, chunk_size: int = 400, overlap: int = 50) -> list[Chunk]:
        content = document.content
        chunks: list[Chunk] = []
        start = 0
        index = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(document_id=document.id, chunk_index=index, content=chunk_text))
                index += 1
            if end == len(content):
                break
            start = max(end - overlap, start + 1)
        return chunks
