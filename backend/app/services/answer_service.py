from dataclasses import dataclass

from app.schemas.chat import Citation
from app.services.llm_service import llm_service


@dataclass
class AnswerResult:
    text: str
    insufficient_evidence: bool
    answer_mode: str
    evidence_summary: list[str]


class AnswerService:
    def generate_answer(self, query: str, citations: list[Citation], grounded_mode: bool = True) -> AnswerResult:
        if not citations:
            return AnswerResult(
                text=f"No indexed content matched '{query}'. Upload documents to improve answers.",
                insufficient_evidence=True,
                answer_mode="insufficient_evidence",
                evidence_summary=[],
            )

        average_score = sum(citation.retrieval_score for citation in citations) / max(1, len(citations))
        top_score = max(citation.retrieval_score for citation in citations)
        score_spread = top_score - min(citation.retrieval_score for citation in citations)
        if grounded_mode and (average_score < 0.35 or top_score < 0.45):
            return AnswerResult(
                text=(
                    "I do not have enough grounded evidence in the indexed documents to answer reliably. "
                    "Try rephrasing your question or uploading more relevant sources."
                ),
                insufficient_evidence=True,
                answer_mode="insufficient_evidence",
                evidence_summary=[],
            )
        if grounded_mode and len(citations) < 2 and score_spread < 0.05:
            return AnswerResult(
                text=(
                    "I found only limited corroborating evidence for this question. "
                    "Please refine the query or provide additional sources."
                ),
                insufficient_evidence=True,
                answer_mode="low_confidence_fallback",
                evidence_summary=[],
            )
        generation = llm_service.generate_grounded_answer(query, citations)
        sources = ", ".join(sorted({citation.document_title for citation in citations}))
        return AnswerResult(
            text=(
                f"{generation.text}\n\nSources consulted: {sources}."
            ),
            insufficient_evidence=False,
            answer_mode=generation.mode,
            evidence_summary=generation.evidence_summary,
        )
