from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession, User
from app.schemas.chat import Citation
from app.services.answer_service import AnswerService
from app.services.retrieval_service import RetrievalService
from app.services.text_utils import tokenize


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
        retrieved = self.retrieval_service.retrieve(query_text, organization_id=user.organization_id)

        citations: list[Citation] = []
        for chunk, score in retrieved:
            preview_text, highlight_start, highlight_end = self._build_source_preview(chunk.content, query_text)
            citations.append(
                Citation(
                    document_id=chunk.document_id,
                    document_title=chunk.document.title,
                    chunk_id=chunk.id,
                    snippet=preview_text[:180],
                    source_preview=preview_text,
                    highlight_start=highlight_start,
                    highlight_end=highlight_end,
                    retrieval_score=round(score.rerank_score or score.score, 4),
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

    def _build_source_preview(self, content: str, query: str, window: int = 220) -> tuple[str, int, int]:
        terms = tokenize(query)
        content_lower = content.lower()

        best_match_start = None
        best_match_len = 0
        for term in terms:
            index = content_lower.find(term)
            if index >= 0:
                if best_match_start is None or index < best_match_start:
                    best_match_start = index
                    best_match_len = len(term)

        if best_match_start is None:
            preview = content[:window]
            highlight_end = min(len(preview), max(1, len(preview) // 4))
            return preview, 0, highlight_end

        preview_start = max(0, best_match_start - (window // 3))
        preview_end = min(len(content), preview_start + window)
        preview = content[preview_start:preview_end]
        highlight_start = max(0, best_match_start - preview_start)
        highlight_end = min(len(preview), highlight_start + best_match_len)
        return preview, highlight_start, max(highlight_start + 1, highlight_end)
