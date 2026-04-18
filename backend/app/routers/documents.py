from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import Role, User
from app.routers.deps import get_current_user, require_role
from app.schemas.document import DocumentIngestResponse
from app.services.document_service import ingest_document

router = APIRouter(prefix="/documents")


@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_document(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    title: str = Form(...),
    text_input: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> DocumentIngestResponse:
    require_role(current_user, {Role.admin, Role.member})

    file_bytes: bytes | None = None
    filename: str | None = None
    if file:
        filename = file.filename
        file_bytes = await file.read()

    try:
        return ingest_document(
            db=db,
            user=current_user,
            title=title,
            text_input=text_input,
            file_bytes=file_bytes,
            filename=filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
