from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentAccess(Base):
    __tablename__ = "document_access"
    __table_args__ = (UniqueConstraint("document_id", "user_id", name="uq_document_access_document_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    permission: Mapped[str] = mapped_column(String(20), nullable=False, default="read")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document")
    user = relationship("User")
