import logging

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.schemas.chat import ChatQueryResponse, RetrievedChunk
from app.services.retrieval_service import retrieve_top_chunks

logger = logging.getLogger(__name__)


def answer_query(db: Session, user: User, query: str, top_k: int) -> ChatQueryResponse:
    retrieved = retrieve_top_chunks(db, organization_id=user.organization_id, query=query, top_k=top_k)

    session = ChatSession(organization_id=user.organization_id, user_id=user.id, title=query[:60])
    db.add(session)
    db.flush()

    db.add(ChatMessage(session_id=session.id, role="user", content=query))

    if retrieved:
        summary = "\n".join(f"- {result.chunk.content[:120]}" for result in retrieved)
        answer_text = f"Based on retrieved knowledge:\n{summary}"
    else:
        answer_text = "I could not find relevant knowledge yet. Please upload documents first."

    db.add(ChatMessage(session_id=session.id, role="assistant", content=answer_text))
    db.commit()

    response_chunks = [
        RetrievedChunk(
            chunk_id=item.chunk.id,
            document_id=item.chunk.document_id,
            chunk_index=item.chunk.chunk_index,
            score=round(item.score, 4),
            citation_ref=item.chunk.citation_ref,
            excerpt=item.chunk.content[:160],
        )
        for item in retrieved
    ]

    logger.info(
        "Chat query processed",
        extra={
            "user_id": user.id,
            "organization_id": user.organization_id,
        },
    )

    return ChatQueryResponse(
        answer=answer_text,
        citations=[item.citation_ref for item in response_chunks],
        retrieved_chunks=response_chunks,
    )
