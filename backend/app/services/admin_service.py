from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AuditLog, ChatFeedback, ChatMessage, ChatSession, Chunk, Collection, Document, IngestionRun, User


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
        ingestions_queued = (
            self.db.query(func.count(IngestionRun.id))
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.organization_id == organization_id, IngestionRun.status == "queued")
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
            "ingestions_queued": int(ingestions_queued),
            "ingestions_completed": int(ingestions_completed),
            "ingestions_failed": int(ingestions_failed),
        }

    def get_top_documents_by_chunk_count(self, organization_id: int, limit: int = 5) -> list[dict[str, int | str]]:
        rows = (
            self.db.query(
                Document.id.label("document_id"),
                Document.title.label("title"),
                func.count(Chunk.id).label("indexed_chunks"),
            )
            .join(Chunk, Chunk.document_id == Document.id)
            .filter(Document.organization_id == organization_id)
            .group_by(Document.id, Document.title)
            .order_by(func.count(Chunk.id).desc(), Document.id.asc())
            .limit(limit)
            .all()
        )
        return [
            {"document_id": int(row.document_id), "title": row.title, "indexed_chunks": int(row.indexed_chunks)}
            for row in rows
        ]

    def get_ingestion_status_breakdown(self, organization_id: int) -> list[dict[str, int | str]]:
        rows = (
            self.db.query(IngestionRun.status.label("status"), func.count(IngestionRun.id).label("count"))
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.organization_id == organization_id)
            .group_by(IngestionRun.status)
            .all()
        )
        return [{"status": row.status, "count": int(row.count)} for row in rows]

    def get_audit_logs(self, organization_id: int, limit: int = 50) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_feedback_summary(self, organization_id: int) -> dict[str, int | float]:
        base_query = (
            self.db.query(ChatFeedback)
            .join(User, ChatFeedback.user_id == User.id)
            .filter(User.organization_id == organization_id)
        )
        total_feedback = base_query.count()
        positive_feedback = base_query.filter(ChatFeedback.rating > 0).count()
        negative_feedback = base_query.filter(ChatFeedback.rating < 0).count()
        positive_ratio = positive_feedback / max(1, total_feedback)
        return {
            "total_feedback": int(total_feedback),
            "positive_feedback": int(positive_feedback),
            "negative_feedback": int(negative_feedback),
            "positive_ratio": round(positive_ratio, 4),
        }

    def get_collection_summary(self, organization_id: int) -> list[dict[str, int | str]]:
        rows = (
            self.db.query(
                Collection.id.label("collection_id"),
                Collection.name.label("name"),
                func.count(Document.id).label("documents_count"),
            )
            .outerjoin(Document, Document.collection_id == Collection.id)
            .filter(Collection.organization_id == organization_id)
            .group_by(Collection.id, Collection.name)
            .order_by(func.count(Document.id).desc(), Collection.id.asc())
            .all()
        )
        return [
            {
                "collection_id": int(row.collection_id),
                "name": row.name,
                "documents_count": int(row.documents_count),
            }
            for row in rows
        ]
