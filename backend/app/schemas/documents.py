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
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    content: str
    chunks: list[ChunkResponse]
