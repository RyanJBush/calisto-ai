from datetime import datetime

from pydantic import BaseModel


class DocumentUploadRequest(BaseModel):
    title: str
    content: str | None = None
    source_name: str | None = None
    file_type: str = "txt"
    file_data_base64: str | None = None
    redact_pii: bool = False
    collection_id: int | None = None


class ChunkPreviewRequest(BaseModel):
    title: str = "Preview"
    content: str | None = None
    file_type: str = "txt"
    file_data_base64: str | None = None
    chunk_size: int = 700
    overlap: int = 120


class ChunkPreviewResponse(BaseModel):
    chunk_count: int
    chunks: list[str]


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
    collection_id: int | None = None
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


class CollectionCreateRequest(BaseModel):
    name: str
    description: str | None = None


class CollectionResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentAccessRequest(BaseModel):
    user_id: int
    permission: str = "read"


class DocumentAccessResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    permission: str
    created_at: datetime

    class Config:
        from_attributes = True
