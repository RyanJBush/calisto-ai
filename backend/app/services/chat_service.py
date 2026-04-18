from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession, User
from app.schemas.chat import Citation
from app.services.answer_service import AnswerService
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.answer_service = AnswerService()

    def _get_or_create_session(self, user: User, session_id: int | None) -> ChatSession:
        if session_id is not None:
            existing = self.db.query(ChatSession).filter_by(id=session_id, user_id=user.id).first()
            if existing:
                return existing
        session = ChatSession(user_id=user.id, title="Knowledge Query")
        self.db.add(session)
        self.db.flush()
        return session

    def query(self, user: User, query_text: str, session_id: int | None) -> tuple[ChatSession, str, list[Citation]]:
        session = self._get_or_create_session(user, session_id)
        retrieved = self.retrieval_service.retrieve(query_text)

        citations: list[Citation] = []
        for chunk, _score in retrieved:
            citations.append(
                Citation(
                    document_id=chunk.document_id,
                    document_title=chunk.document.title,
                    chunk_id=chunk.id,
                    snippet=chunk.content[:180],
                )
            )

        answer = self.answer_service.generate_answer(query_text, citations)

        self.db.add(ChatMessage(session_id=session.id, role="user", content=query_text))
        self.db.add(ChatMessage(session_id=session.id, role="assistant", content=answer))
        self.db.commit()
        self.db.refresh(session)
        return session, answer, citations

    def get_history(self, user_id: int) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
