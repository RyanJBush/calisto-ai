from datetime import datetime

from pydantic import BaseModel


class QueryFilters(BaseModel):
    source_name: str | None = None
    document_ids: list[int] | None = None
    collection_id: int | None = None


class ChatQueryRequest(BaseModel):
    query: str
    session_id: int | None = None
    filters: QueryFilters | None = None
    grounded_mode: bool = True


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
    assistant_message_id: int
    answer: str
    answer_mode: str
    evidence_summary: list[str] = []
    rewritten_query: str
    confidence_score: float
    citation_coverage: float
    insufficient_evidence: bool
    latency_breakdown_ms: dict[str, float]
    citations: list[Citation]


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatFeedbackRequest(BaseModel):
    message_id: int
    rating: int
    comment: str | None = None


class ChatFeedbackResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    rating: int
    comment: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
