from datetime import datetime

from pydantic import BaseModel


class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    source_name: str | None = None


class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    title: str
    source_name: str
    version: int
    parent_document_id: int | None = None
    created_at: datetime
    ingestion_status: str
    ingestion_error: str | None = None
    ingestion_attempts: int = 0

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    content: str
    chunks: list[ChunkResponse]


class IngestionRunResponse(BaseModel):
    id: int
    document_id: int
    status: str
    attempts: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
