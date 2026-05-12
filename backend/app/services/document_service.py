import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import Chunk, Collection, Document, DocumentAccess, IngestionRun, User
from app.schemas.documents import DocumentUploadRequest
from app.services.audit_service import AuditService
from app.services.content_extraction_service import ContentExtractionService
from app.services.ingestion_job_service import ingestion_job_service
from app.services.ingestion_service import IngestionService
from app.services.security_text_service import SecurityTextService


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_service = AuditService(db)
        self.security_text_service = SecurityTextService()
        self.content_extraction_service = ContentExtractionService()
        self.ingestion_service = IngestionService()

    def upload_document(self, payload: DocumentUploadRequest, user: User) -> Document:
        source_name = payload.source_name or payload.title
        parsed_content = self.content_extraction_service.parse(
            content=payload.content,
            file_data_base64=payload.file_data_base64,
            file_type=payload.file_type,
        )
        normalized_content = (
            self.security_text_service.redact_pii(parsed_content) if payload.redact_pii else parsed_content
        )
        content_hash = hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()
        duplicate = (
            self.db.query(Document)
            .filter(
                Document.organization_id == user.organization_id,
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
            collection_id=payload.collection_id,
            content=normalized_content,
        )
        if payload.collection_id is not None:
            collection = self.db.get(Collection, payload.collection_id)
            if collection is None or collection.organization_id != user.organization_id:
                raise ValueError("Collection not found for this organization.")
        self.db.add(document)
        self.db.flush()

        ingestion_run = IngestionRun(document_id=document.id, status="queued", attempts=0)
        self.db.add(ingestion_run)
        ingestion_run.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(ingestion_run)

        ingestion_job_service.enqueue(document.id, ingestion_run.id)
        self.audit_service.log(
            organization_id=user.organization_id,
            action="document_upload",
            resource_type="document",
            resource_id=document.id,
            details=f"source={source_name};version={document.version};redact_pii={payload.redact_pii}",
            user=user,
        )
        self.db.commit()

        self.db.refresh(document)
        return document

    def preview_chunks(
        self,
        *,
        title: str,
        content: str | None,
        file_data_base64: str | None,
        file_type: str,
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        parsed_content = self.content_extraction_service.parse(
            content=content,
            file_data_base64=file_data_base64,
            file_type=file_type,
        )
        preview_doc = Document(id=0, organization_id=0, uploaded_by=0, title=title, source_name=title, content_hash="", content=parsed_content, version=1)
        chunks = self.ingestion_service.chunk_document(preview_doc, chunk_size=chunk_size, overlap=overlap)
        return [chunk.content for chunk in chunks]

    def list_documents_for_user(self, user: User) -> list[Document]:
        query = (
            self.db.query(Document)
            .options(joinedload(Document.ingestion_runs))
            .filter(Document.organization_id == user.organization_id)
        )
        if user.role.lower() == "viewer":
            query = query.join(DocumentAccess, DocumentAccess.document_id == Document.id).filter(DocumentAccess.user_id == user.id)
        return query.order_by(Document.created_at.desc()).all()

    def get_document_for_user(self, document_id: int, user: User) -> Document | None:
        query = (
            self.db.query(Document)
            .options(joinedload(Document.chunks), joinedload(Document.ingestion_runs))
            .filter(Document.id == document_id, Document.organization_id == user.organization_id)
        )
        if user.role.lower() == "viewer":
            query = query.join(DocumentAccess, DocumentAccess.document_id == Document.id).filter(DocumentAccess.user_id == user.id)
        return query.first()

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

    def accessible_document_ids(self, user: User) -> list[int]:
        if user.role.lower() != "viewer":
            rows = self.db.query(Document.id).filter(Document.organization_id == user.organization_id).all()
            return [int(row.id) for row in rows]
        rows = (
            self.db.query(Document.id)
            .join(DocumentAccess, DocumentAccess.document_id == Document.id)
            .filter(Document.organization_id == user.organization_id, DocumentAccess.user_id == user.id)
            .all()
        )
        return [int(row.id) for row in rows]

    def create_collection(self, organization_id: int, name: str, description: str | None) -> Collection:
        existing = (
            self.db.query(Collection)
            .filter(Collection.organization_id == organization_id, Collection.name == name)
            .first()
        )
        if existing:
            raise ValueError("Collection with this name already exists.")
        collection = Collection(organization_id=organization_id, name=name, description=description)
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return collection

    def list_collections(self, organization_id: int) -> list[Collection]:
        return (
            self.db.query(Collection)
            .filter(Collection.organization_id == organization_id)
            .order_by(Collection.created_at.desc())
            .all()
        )

    def grant_document_access(
        self,
        organization_id: int,
        document_id: int,
        target_user_id: int,
        permission: str = "read",
    ) -> DocumentAccess:
        document = self.db.query(Document).filter(Document.id == document_id, Document.organization_id == organization_id).first()
        target_user = self.db.query(User).filter(User.id == target_user_id, User.organization_id == organization_id).first()
        if document is None or target_user is None:
            raise ValueError("Document or user not found in this organization.")
        existing = (
            self.db.query(DocumentAccess)
            .filter(DocumentAccess.document_id == document_id, DocumentAccess.user_id == target_user_id)
            .first()
        )
        if existing:
            existing.permission = permission
            access = existing
        else:
            access = DocumentAccess(document_id=document_id, user_id=target_user_id, permission=permission)
            self.db.add(access)
        self.db.commit()
        self.db.refresh(access)
        return access

    def revoke_document_access(self, organization_id: int, document_id: int, target_user_id: int) -> None:
        access = (
            self.db.query(DocumentAccess)
            .join(Document, DocumentAccess.document_id == Document.id)
            .filter(
                Document.organization_id == organization_id,
                DocumentAccess.document_id == document_id,
                DocumentAccess.user_id == target_user_id,
            )
            .first()
        )
        if access is None:
            raise ValueError("Document access grant not found.")
        self.db.delete(access)
        self.db.commit()
