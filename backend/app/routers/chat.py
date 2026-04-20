from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.chat import ChatMessageResponse, ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
def query(
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatQueryResponse:
    service = ChatService(db)
    session, answer, citations = service.query(user, payload.query, payload.session_id, payload.filters)
    return ChatQueryResponse(session_id=session.id, answer=answer, citations=citations)


@router.get("/history", response_model=list[ChatMessageResponse])
def history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ChatMessageResponse]:
    service = ChatService(db)
    messages = service.get_history(user.id)
    return [ChatMessageResponse.model_validate(message) for message in messages]
