import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_and_issue_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    try:
        token, user = authenticate_and_issue_token(db, payload.email, payload.password)
    except ValueError as exc:
        logger.info("Login failed", extra={"path": "/auth/login", "method": "POST"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc

    logger.info(
        "Login succeeded",
        extra={
            "path": "/auth/login",
            "method": "POST",
            "user_id": user.id,
            "organization_id": user.organization_id,
        },
    )
    return TokenResponse(
        access_token=token,
        role=user.role.value,
        organization_id=user.organization_id,
    )
