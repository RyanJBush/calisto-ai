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
