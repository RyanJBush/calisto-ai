from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.chat import (
    ChatFeedbackRequest,
    ChatFeedbackResponse,
    ChatMessageResponse,
    ChatQueryRequest,
    ChatQueryResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
def query(
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatQueryResponse:
    service = ChatService(db)
    (
        session,
        assistant_message_id,
        answer,
        citations,
        insufficient_evidence,
        confidence_score,
        citation_coverage,
        rewritten_query,
        latency_breakdown_ms,
    ) = service.query(
        user,
        payload.query,
        payload.session_id,
        payload.filters,
        grounded_mode=payload.grounded_mode,
    )
    return ChatQueryResponse(
        session_id=session.id,
        assistant_message_id=assistant_message_id,
        answer=answer,
        rewritten_query=rewritten_query,
        confidence_score=confidence_score,
        citation_coverage=citation_coverage,
        insufficient_evidence=insufficient_evidence,
        latency_breakdown_ms=latency_breakdown_ms,
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


@router.post("/feedback", response_model=ChatFeedbackResponse)
def submit_feedback(
    payload: ChatFeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatFeedbackResponse:
    service = ChatService(db)
    try:
        feedback = service.submit_feedback(
            user=user,
            message_id=payload.message_id,
            rating=payload.rating,
            comment=payload.comment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ChatFeedbackResponse.model_validate(feedback)
