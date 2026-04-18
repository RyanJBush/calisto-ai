from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthTokenResponse, LoginRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    service = AuthService(db)
    token = service.authenticate(payload.email, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return AuthTokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)
