from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.documents import (
    ChunkPreviewRequest,
    ChunkPreviewResponse,
    CollectionCreateRequest,
    CollectionResponse,
    DocumentAccessRequest,
    DocumentAccessResponse,
    DocumentDetailResponse,
    DocumentResponse,
    DocumentUploadRequest,
    IngestionRunResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    payload: DocumentUploadRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "member")),
) -> DocumentResponse:
    service = DocumentService(db)
    try:
        document = service.upload_document(payload, user)
    except ValueError as exc:
        message = str(exc)
        status_code = status.HTTP_409_CONFLICT if "Duplicate document" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc
    return DocumentResponse.model_validate(document)


@router.post("/preview-chunks", response_model=ChunkPreviewResponse)
def preview_chunks(
    payload: ChunkPreviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "member")),
) -> ChunkPreviewResponse:
    service = DocumentService(db)
    try:
        chunks = service.preview_chunks(
            title=payload.title,
            content=payload.content,
            file_data_base64=payload.file_data_base64,
            file_type=payload.file_type,
            chunk_size=payload.chunk_size,
            overlap=payload.overlap,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ChunkPreviewResponse(chunk_count=len(chunks), chunks=chunks)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
    service = DocumentService(db)
    documents = service.list_documents_for_user(user)
    return [DocumentResponse.model_validate(document) for document in documents]


@router.post("/collections", response_model=CollectionResponse)
def create_collection(
    payload: CollectionCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "member")),
) -> CollectionResponse:
    service = DocumentService(db)
    try:
        collection = service.create_collection(user.organization_id, payload.name, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return CollectionResponse.model_validate(collection)


@router.get("/collections", response_model=list[CollectionResponse])
def list_collections(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CollectionResponse]:
    service = DocumentService(db)
    collections = service.list_collections(user.organization_id)
    return [CollectionResponse.model_validate(item) for item in collections]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentDetailResponse:
    service = DocumentService(db)
    document = service.get_document_for_user(document_id, user)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentDetailResponse.model_validate(document)


@router.get("/{document_id}/ingestion-runs", response_model=list[IngestionRunResponse])
def get_ingestion_runs(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[IngestionRunResponse]:
    service = DocumentService(db)
    runs = service.get_ingestion_runs(document_id=document_id, organization_id=user.organization_id)
    return [IngestionRunResponse.model_validate(run) for run in runs]


@router.post("/{document_id}/access", response_model=DocumentAccessResponse)
def grant_document_access(
    document_id: int,
    payload: DocumentAccessRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> DocumentAccessResponse:
    service = DocumentService(db)
    try:
        access = service.grant_document_access(
            organization_id=user.organization_id,
            document_id=document_id,
            target_user_id=payload.user_id,
            permission=payload.permission,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DocumentAccessResponse.model_validate(access)


@router.delete("/{document_id}/access/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_document_access(
    document_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> None:
    service = DocumentService(db)
    try:
        service.revoke_document_access(user.organization_id, document_id, target_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
