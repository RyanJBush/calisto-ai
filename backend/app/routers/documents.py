from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.documents import (
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
    service = DocumentService(db)
    documents = service.list_documents_for_org(user.organization_id)
    return [DocumentResponse.model_validate(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentDetailResponse:
    service = DocumentService(db)
    document = service.get_document_for_org(document_id, user.organization_id)
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
