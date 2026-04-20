from datetime import datetime

from pydantic import BaseModel


class AdminAnalyticsSummaryResponse(BaseModel):
    documents_total: int
    chunks_total: int
    chat_sessions_total: int
    queries_total: int
    ingestions_processing: int
    ingestions_queued: int
    ingestions_completed: int
    ingestions_failed: int


class AdminTopDocumentResponse(BaseModel):
    document_id: int
    title: str
    indexed_chunks: int


class AdminIngestionStatusResponse(BaseModel):
    status: str
    count: int


class AuditLogResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: int | None
    details: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    positive_ratio: float


class BenchmarkRunResponse(BaseModel):
    cases_total: int
    cases_passed: int
    pass_rate: float
    average_case_score: float


class CollectionSummaryResponse(BaseModel):
    collection_id: int
    name: str
    documents_count: int
