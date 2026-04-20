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
    session, answer, citations, insufficient_evidence, confidence_score, citation_coverage, rewritten_query = (
        service.query(
            user,
            payload.query,
            payload.session_id,
            payload.filters,
            grounded_mode=payload.grounded_mode,
        )
    )
    return ChatQueryResponse(
        session_id=session.id,
        answer=answer,
        rewritten_query=rewritten_query,
        confidence_score=confidence_score,
        citation_coverage=citation_coverage,
        insufficient_evidence=insufficient_evidence,
        citations=citations,
    )


@router.get("/history", response_model=list[ChatMessageResponse])
def history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ChatMessageResponse]:
    service = ChatService(db)
    messages = service.get_history(user.id)
    return [ChatMessageResponse.model_validate(message) for message in messages]
