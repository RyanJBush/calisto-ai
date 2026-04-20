from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    parent_document = relationship("Document", remote_side=[id], back_populates="versions")
    versions = relationship("Document", back_populates="parent_document")
    ingestion_runs = relationship(
        "IngestionRun",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="IngestionRun.id",
    )

    @property
    def ingestion_status(self) -> str:
        if not self.ingestion_runs:
            return "pending"
        return self.ingestion_runs[-1].status

    @property
    def ingestion_error(self) -> str | None:
        if not self.ingestion_runs:
            return None
        return self.ingestion_runs[-1].error_message

    @property
    def ingestion_attempts(self) -> int:
        if not self.ingestion_runs:
            return 0
        return self.ingestion_runs[-1].attempts
