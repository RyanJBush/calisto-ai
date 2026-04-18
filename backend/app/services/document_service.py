import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.document import DocumentChunkSummary, DocumentIngestResponse
from app.services.embedding_service import EmbeddingService
from app.services.text_processing_service import chunk_text, extract_text

logger = logging.getLogger(__name__)


def ingest_document(
    db: Session,
    user: User,
    title: str,
    text_input: str | None,
    file_bytes: bytes | None,
    filename: str | None,
) -> DocumentIngestResponse:
    text = extract_text(text_input=text_input, file_bytes=file_bytes, filename=filename)

    document = Document(
        organization_id=user.organization_id,
        uploaded_by_user_id=user.id,
        title=title,
        source_type="text_input" if text_input else "file_upload",
        content=text,
    )
    db.add(document)
    db.flush()

    embedder = EmbeddingService()
    chunks = chunk_text(
        text,
        chunk_size=settings.default_chunk_size,
        overlap=settings.default_chunk_overlap,
    )

    chunk_summaries: list[DocumentChunkSummary] = []
    for index, chunk in enumerate(chunks):
        citation_ref = f"doc:{document.id}:chunk:{index}"
        db_chunk = DocumentChunk(
            document_id=document.id,
            organization_id=user.organization_id,
            chunk_index=index,
            content=chunk,
            embedding=embedder.embed_text(chunk),
            metadata_json={"title": title, "filename": filename or "n/a"},
            citation_ref=citation_ref,
        )
        db.add(db_chunk)
        db.flush()
        chunk_summaries.append(
            DocumentChunkSummary(
                chunk_id=db_chunk.id,
                chunk_index=index,
                citation_ref=citation_ref,
            )
        )

    db.commit()

    logger.info(
        "Document ingested",
        extra={
            "user_id": user.id,
            "organization_id": user.organization_id,
            "document_id": document.id,
        },
    )

    return DocumentIngestResponse(
        document_id=document.id,
        title=document.title,
        chunk_count=len(chunk_summaries),
        chunks=chunk_summaries,
    )
