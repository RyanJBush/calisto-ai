from pydantic import BaseModel


class DocumentChunkSummary(BaseModel):
    chunk_id: int
    chunk_index: int
    citation_ref: str


class DocumentIngestResponse(BaseModel):
    document_id: int
    title: str
    chunk_count: int
    chunks: list[DocumentChunkSummary]
