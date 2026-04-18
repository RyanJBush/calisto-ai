from app.schemas.chat import Citation


class AnswerService:
    def generate_answer(self, query: str, citations: list[Citation]) -> str:
        if not citations:
            return f"No indexed content matched '{query}'. Upload documents to improve answers."
        sources = ", ".join(sorted({citation.document_title for citation in citations}))
        return (
            f"Based on the retrieved knowledge base excerpts, here is a grounded response to '{query}'. "
            f"Sources consulted: {sources}."
        )
