from datetime import datetime

from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    query: str
    session_id: int | None = None


class Citation(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    snippet: str


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
