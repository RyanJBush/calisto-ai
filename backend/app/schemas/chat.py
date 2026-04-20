from datetime import datetime

from pydantic import BaseModel


class QueryFilters(BaseModel):
    source_name: str | None = None
    document_ids: list[int] | None = None


class ChatQueryRequest(BaseModel):
    query: str
    session_id: int | None = None
    filters: QueryFilters | None = None


class Citation(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    snippet: str
    source_preview: str
    highlight_start: int
    highlight_end: int
    highlight_ranges: list[tuple[int, int]] = []
    retrieval_score: float


class ChatQueryResponse(BaseModel):
    session_id: int
    answer: str
    citations: list[Citation]


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
