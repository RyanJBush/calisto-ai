from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.documents import (
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
from app.services.file_parser_service import file_parser_service

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


@router.post("/upload-file", response_model=DocumentResponse)
async def upload_document_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    source_name: str | None = Form(default=None),
    redact_pii: bool = Form(default=False),
    collection_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "member")),
) -> DocumentResponse:
    payload = await file.read()
    try:
        content = file_parser_service.extract_text(
            filename=file.filename or title,
            content_type=file.content_type,
            payload=payload,
        )
        document = DocumentService(db).upload_document_content(
            title=title,
            content=content,
            source_name=source_name or file.filename,
            redact_pii=redact_pii,
            collection_id=collection_id,
            user=user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
    service = DocumentService(db)
    documents = service.list_documents_for_user(user)
    return [DocumentResponse.model_validate(document) for document in documents]


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


@router.post("/{document_id}/retry-ingestion", response_model=IngestionRunResponse)
def retry_ingestion(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "member")),
) -> IngestionRunResponse:
    service = DocumentService(db)
    try:
        run = service.retry_ingestion(document_id=document_id, organization_id=user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return IngestionRunResponse.model_validate(run)
