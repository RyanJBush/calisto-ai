from dataclasses import dataclass

from app.schemas.chat import Citation


@dataclass
class AnswerResult:
    text: str
    insufficient_evidence: bool


class AnswerService:
    def generate_answer(self, query: str, citations: list[Citation], grounded_mode: bool = True) -> AnswerResult:
        if not citations:
            return AnswerResult(
                text=f"No indexed content matched '{query}'. Upload documents to improve answers.",
                insufficient_evidence=True,
            )

        average_score = sum(citation.retrieval_score for citation in citations) / max(1, len(citations))
        if grounded_mode and average_score < 0.35:
            return AnswerResult(
                text=(
                    "I do not have enough grounded evidence in the indexed documents to answer reliably. "
                    "Try rephrasing your question or uploading more relevant sources."
                ),
                insufficient_evidence=True,
            )

        sources = ", ".join(sorted({citation.document_title for citation in citations}))
        return AnswerResult(
            text=(
                f"Based on the retrieved knowledge base excerpts, here is a grounded response to '{query}'. "
                f"Sources consulted: {sources}."
            ),
            insufficient_evidence=False,
        )
