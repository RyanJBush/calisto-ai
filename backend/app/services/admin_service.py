from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession, Chunk, Document, IngestionRun, User


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_analytics_summary(self, organization_id: int) -> dict[str, int]:
        total_documents = (
            self.db.query(func.count(Document.id)).filter(Document.organization_id == organization_id).scalar() or 0
        )
        total_chunks = (
            self.db.query(func.count(Chunk.id))
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.organization_id == organization_id)
            .scalar()
            or 0
        )
        total_chat_sessions = (
            self.db.query(func.count(ChatSession.id))
            .join(User, ChatSession.user_id == User.id)
            .filter(User.organization_id == organization_id)
            .scalar()
            or 0
        )
        total_queries = (
            self.db.query(func.count(ChatMessage.id))
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .join(User, ChatSession.user_id == User.id)
            .filter(User.organization_id == organization_id, ChatMessage.role == "user")
            .scalar()
            or 0
        )
        ingestions_processing = (
            self.db.query(func.count(IngestionRun.id))
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.organization_id == organization_id, IngestionRun.status == "processing")
            .scalar()
            or 0
        )
        ingestions_completed = (
            self.db.query(func.count(IngestionRun.id))
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.organization_id == organization_id, IngestionRun.status == "completed")
            .scalar()
            or 0
        )
        ingestions_failed = (
            self.db.query(func.count(IngestionRun.id))
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.organization_id == organization_id, IngestionRun.status == "failed")
            .scalar()
            or 0
        )
        return {
            "documents_total": int(total_documents),
            "chunks_total": int(total_chunks),
            "chat_sessions_total": int(total_chat_sessions),
            "queries_total": int(total_queries),
            "ingestions_processing": int(ingestions_processing),
            "ingestions_completed": int(ingestions_completed),
            "ingestions_failed": int(ingestions_failed),
        }
