import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import Chunk, Document, IngestionRun, User
from app.schemas.documents import DocumentUploadRequest
from app.services.ingestion_job_service import ingestion_job_service


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upload_document(self, payload: DocumentUploadRequest, user: User) -> Document:
        source_name = payload.source_name or payload.title
        content_hash = hashlib.sha256(payload.content.encode("utf-8")).hexdigest()
        duplicate = (
            self.db.query(Document)
            .filter(
                Document.organization_id == user.organization_id,
                Document.source_name == source_name,
                Document.content_hash == content_hash,
            )
            .first()
        )
        if duplicate:
            raise ValueError(f"Duplicate document detected for source '{source_name}' (document_id={duplicate.id}).")

        latest_version = (
            self.db.query(Document)
            .filter(Document.organization_id == user.organization_id, Document.source_name == source_name)
            .order_by(Document.version.desc(), Document.id.desc())
            .first()
        )
        parent_document_id = latest_version.parent_document_id if latest_version else None
        if latest_version and parent_document_id is None:
            parent_document_id = latest_version.id
        next_version = 1 if latest_version is None else latest_version.version + 1

        document = Document(
            organization_id=user.organization_id,
            uploaded_by=user.id,
            title=payload.title,
            source_name=source_name,
            content_hash=content_hash,
            version=next_version,
            parent_document_id=parent_document_id,
            content=payload.content,
        )
        self.db.add(document)
        self.db.flush()

        ingestion_run = IngestionRun(document_id=document.id, status="queued", attempts=0)
        self.db.add(ingestion_run)
        ingestion_run.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(ingestion_run)

        ingestion_job_service.enqueue(document.id, ingestion_run.id)

        self.db.refresh(document)
        return document

    def list_documents_for_org(self, organization_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .options(joinedload(Document.ingestion_runs))
            .filter(Document.organization_id == organization_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_document_for_org(self, document_id: int, organization_id: int) -> Document | None:
        return (
            self.db.query(Document)
            .options(joinedload(Document.chunks), joinedload(Document.ingestion_runs))
            .filter(Document.id == document_id, Document.organization_id == organization_id)
            .first()
        )

    def get_ingestion_runs(self, document_id: int, organization_id: int) -> list[IngestionRun]:
        return (
            self.db.query(IngestionRun)
            .join(Document, IngestionRun.document_id == Document.id)
            .filter(Document.id == document_id, Document.organization_id == organization_id)
            .order_by(IngestionRun.id.desc())
            .all()
        )

    def get_chunk(self, chunk_id: int) -> Chunk | None:
        return self.db.get(Chunk, chunk_id)
