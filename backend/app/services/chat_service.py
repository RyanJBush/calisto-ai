import time

from sqlalchemy.orm import Session

from app.models import ChatFeedback, ChatMessage, ChatSession, User
from app.schemas.chat import Citation, QueryFilters
from app.services.audit_service import AuditService
from app.services.answer_service import AnswerService
from app.services.document_service import DocumentService
from app.services.query_rewrite_service import QueryRewriteService
from app.services.retrieval_service import RetrievalFilters, RetrievalService
from app.services.security_text_service import SecurityTextService
from app.services.text_utils import tokenize

DEFAULT_PREVIEW_HIGHLIGHT_RATIO = 0.25


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.answer_service = AnswerService()
        self.query_rewrite_service = QueryRewriteService()
        self.audit_service = AuditService(db)
        self.security_text_service = SecurityTextService()
        self.document_service = DocumentService(db)

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
        grounded_mode: bool = True,
        top_k: int = 3,
    ) -> tuple[ChatSession, int, str, str, list[str], list[str], list[Citation], bool, float, float, str, dict[str, float]]:
    ) -> tuple[ChatSession, int, str, str, list[str], list[Citation], bool, float, float, str, dict[str, float]]:
        session = self._get_or_create_session(user, session_id)
        total_start = time.perf_counter()
        rewrite_start = time.perf_counter()
        rewritten_query = self.query_rewrite_service.rewrite(query_text)
        rewrite_ms = (time.perf_counter() - rewrite_start) * 1000
        accessible_ids = self.document_service.accessible_document_ids(user)
        requested_ids = filters.document_ids if filters and filters.document_ids else None
        effective_ids = (
            [doc_id for doc_id in accessible_ids if requested_ids is None or doc_id in requested_ids]
            if accessible_ids
            else []
        )
        retrieval_filters = RetrievalFilters(
            source_name=filters.source_name if filters else None,
            document_ids=effective_ids,
            collection_id=filters.collection_id if filters else None,
            section=filters.section if filters else None,
            tags=filters.tags if filters else None,
        )
        retrieval_start = time.perf_counter()
        retrieved = self.retrieval_service.retrieve(
            rewritten_query,
            organization_id=user.organization_id,
            filters=retrieval_filters,
            top_k=max(1, min(12, top_k)),
        )
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        citations: list[Citation] = []
        for chunk, score in retrieved:
            preview_text, highlight_start, highlight_end, highlight_ranges = self._build_source_preview(
                self.security_text_service.sanitize_prompt_injection(chunk.content),
                rewritten_query,
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
                    section_label=self._derive_section_label(chunk.content),
                    evidence=chunk.content[:500],
                )
            )

        answer_start = time.perf_counter()
        answer_result = self.answer_service.generate_answer(rewritten_query, citations, grounded_mode=grounded_mode)
        answer_ms = (time.perf_counter() - answer_start) * 1000
        citation_coverage = self._compute_citation_coverage(rewritten_query, citations)
        confidence_score = self._compute_confidence(citations, citation_coverage, answer_result.insufficient_evidence)
        source_alignment = self._build_source_alignment(answer_result.text, citations)
        total_ms = (time.perf_counter() - total_start) * 1000

        self.db.add(ChatMessage(session_id=session.id, role="user", content=query_text))
        assistant_message = ChatMessage(session_id=session.id, role="assistant", content=answer_result.text)
        self.db.add(assistant_message)
        self.db.flush()
        self.audit_service.log(
            organization_id=user.organization_id,
            action="chat_query",
            resource_type="chat_session",
            resource_id=session.id,
            details=(
                f"rewritten_query={rewritten_query};citations={len(citations)};"
                f"confidence={confidence_score};insufficient_evidence={answer_result.insufficient_evidence};"
                f"latency_ms_total={round(total_ms, 2)}"
            ),
            user=user,
        )
        self.db.commit()
        self.db.refresh(session)
        return (
            session,
            assistant_message.id,
            answer_result.text,
            answer_result.answer_mode,
            answer_result.evidence_summary,
            source_alignment,
            citations,
            answer_result.insufficient_evidence,
            confidence_score,
            citation_coverage,
            rewritten_query,
            {
                "rewrite": round(rewrite_ms, 2),
                "retrieval": round(retrieval_ms, 2),
                "answer": round(answer_ms, 2),
                "total": round(total_ms, 2),
            },
        )

    def submit_feedback(self, user: User, message_id: int, rating: int, comment: str | None) -> ChatFeedback:
        rating_value = 1 if rating > 0 else -1
        message = (
            self.db.query(ChatMessage)
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .filter(ChatMessage.id == message_id, ChatSession.user_id == user.id, ChatMessage.role == "assistant")
            .first()
        )
        if message is None:
            raise ValueError("Assistant message not found for this user.")

        feedback = ChatFeedback(message_id=message_id, user_id=user.id, rating=rating_value, comment=comment)
        self.db.add(feedback)
        self.audit_service.log(
            organization_id=user.organization_id,
            action="chat_feedback",
            resource_type="chat_message",
            resource_id=message_id,
            details=f"rating={rating_value}",
            user=user,
        )
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

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

    def _compute_citation_coverage(self, query: str, citations: list[Citation]) -> float:
        query_terms = set(tokenize(query))
        if not query_terms or not citations:
            return 0.0

        covered_terms: set[str] = set()
        for citation in citations:
            citation_terms = set(tokenize(citation.source_preview))
            covered_terms |= query_terms & citation_terms

        return round(min(1.0, len(covered_terms) / max(1, len(query_terms))), 4)

    def _compute_confidence(
        self,
        citations: list[Citation],
        citation_coverage: float,
        insufficient_evidence: bool,
    ) -> float:
        if insufficient_evidence or not citations:
            return 0.0

        average_retrieval = sum(citation.retrieval_score for citation in citations) / max(1, len(citations))
        return round(min(1.0, (average_retrieval * 0.7) + (citation_coverage * 0.3)), 4)

    def _build_source_alignment(self, answer_text: str, citations: list[Citation]) -> list[str]:
        alignments: list[str] = []
        lowered = answer_text.lower()
        for citation in citations[:5]:
            section = citation.section_label or "general"
            marker = f"{citation.document_title.lower()}"
            if marker in lowered:
                alignments.append(f"{citation.document_title} ({section}) explicitly referenced in answer")
            else:
                alignments.append(f"{citation.document_title} ({section}) supports cited claims via chunk {citation.chunk_id}")
        return alignments

    def _derive_section_label(self, content: str) -> str | None:
        first_line = next((line.strip() for line in content.splitlines() if line.strip()), "")
        if not first_line:
            return None
        if first_line.startswith(("#", "##", "###")):
            return first_line.lstrip("#").strip()[:120]
        if ":" in first_line and len(first_line) < 120:
            return first_line[:120]
        return first_line[:80]
