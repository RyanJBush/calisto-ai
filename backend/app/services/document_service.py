from sqlalchemy.orm import Session

from app.models import Chunk, Document, User
from app.schemas.documents import DocumentUploadRequest
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.vector_store import vector_store


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.ingestion_service = IngestionService()
        self.embedding_service = EmbeddingService()

    def upload_document(self, payload: DocumentUploadRequest, user: User) -> Document:
        source_name = payload.source_name or payload.title
        document = Document(
            organization_id=user.organization_id,
            uploaded_by=user.id,
            title=payload.title,
            source_name=source_name,
            content=payload.content,
        )
        self.db.add(document)
        self.db.flush()

        chunks = self.ingestion_service.chunk_document(document)
        for chunk in chunks:
            self.db.add(chunk)
        self.db.flush()

        for chunk in chunks:
            vector = self.embedding_service.embed_text(chunk.content)
            vector_store.add(chunk.id, vector)

        self.db.commit()
        self.db.refresh(document)
        return document

    def list_documents_for_org(self, organization_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.organization_id == organization_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_document_for_org(self, document_id: int, organization_id: int) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.organization_id == organization_id)
            .first()
        )

    def get_chunk(self, chunk_id: int) -> Chunk | None:
        return self.db.get(Chunk, chunk_id)
