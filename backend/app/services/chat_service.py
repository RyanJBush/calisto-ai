from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession, User
from app.schemas.chat import Citation, QueryFilters
from app.services.answer_service import AnswerService
from app.services.retrieval_service import RetrievalFilters, RetrievalService
from app.services.text_utils import tokenize

DEFAULT_PREVIEW_HIGHLIGHT_RATIO = 0.25


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

    def query(
        self,
        user: User,
        query_text: str,
        session_id: int | None,
        filters: QueryFilters | None = None,
    ) -> tuple[ChatSession, str, list[Citation]]:
        session = self._get_or_create_session(user, session_id)
        retrieval_filters = RetrievalFilters(
            source_name=filters.source_name if filters else None,
            document_ids=filters.document_ids if filters else None,
        )
        retrieved = self.retrieval_service.retrieve(
            query_text,
            organization_id=user.organization_id,
            filters=retrieval_filters,
        )

        citations: list[Citation] = []
        for chunk, score in retrieved:
            preview_text, highlight_start, highlight_end, highlight_ranges = self._build_source_preview(
                chunk.content, query_text
            )
            citations.append(
                Citation(
                    document_id=chunk.document_id,
                    document_title=chunk.document.title,
                    chunk_id=chunk.id,
                    snippet=preview_text[:180],
                    source_preview=preview_text,
                    highlight_start=highlight_start,
                    highlight_end=highlight_end,
                    highlight_ranges=highlight_ranges,
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

    def _build_source_preview(
        self, content: str, query: str, max_preview_chars: int = 220
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        terms = tokenize(query)
        content_lower = content.lower()

        matches: list[tuple[int, int]] = []
        for term in sorted(set(terms), key=len, reverse=True):
            start_index = 0
            while start_index < len(content_lower):
                index = content_lower.find(term, start_index)
                if index < 0:
                    break
                matches.append((index, index + len(term)))
                start_index = index + len(term)

        best_match_start = min((start for start, _end in matches), default=None)

        if best_match_start is None:
            preview = content[:max_preview_chars]
            highlight_end = min(len(preview), max(1, int(len(preview) * DEFAULT_PREVIEW_HIGHLIGHT_RATIO)))
            return preview, 0, highlight_end, [(0, highlight_end)]

        preview_start = max(0, best_match_start - (max_preview_chars // 3))
        preview_end = min(len(content), preview_start + max_preview_chars)
        preview = content[preview_start:preview_end]
        preview_ranges: list[tuple[int, int]] = []
        for start, end in matches:
            if end <= preview_start or start >= preview_end:
                continue
            clipped_start = max(0, start - preview_start)
            clipped_end = min(len(preview), end - preview_start)
            if clipped_end > clipped_start:
                preview_ranges.append((clipped_start, clipped_end))

        preview_ranges.sort(key=lambda item: item[0])
        if not preview_ranges:
            highlight_start = max(0, best_match_start - preview_start)
            highlight_end = min(len(preview), highlight_start + max(1, int(len(query) * DEFAULT_PREVIEW_HIGHLIGHT_RATIO)))
            return preview, highlight_start, max(highlight_start + 1, highlight_end), [(highlight_start, highlight_end)]

        highlight_start, highlight_end = preview_ranges[0]
        return preview, highlight_start, highlight_end, preview_ranges
