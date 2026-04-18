from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import answer_query

router = APIRouter(prefix="/chat")


@router.post("/query", response_model=ChatQueryResponse)
def query_chat(
    payload: ChatQueryRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatQueryResponse:
    return answer_query(db=db, user=current_user, query=payload.query, top_k=payload.top_k)
