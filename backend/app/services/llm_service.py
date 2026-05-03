from dataclasses import dataclass

from app.config import get_settings
from app.schemas.chat import Citation


@dataclass
class LLMGeneration:
    text: str
    mode: str
    evidence_summary: list[str]


class HeuristicGroundedLLM:
    """Heuristic-based grounded answer generator.

    Composes a structured, readable answer directly from the top retrieved
    evidence chunks without calling an external LLM.  Every claim is tied
    to a specific chunk reference so the answer is fully traceable.
    """

    def generate(self, query: str, citations: list[Citation]) -> LLMGeneration:
        ordered = sorted(citations, key=lambda c: c.retrieval_score, reverse=True)
        top = ordered[:3]

        evidence_summary = [
            f"{c.document_title}: {c.snippet.strip()}" for c in top if c.snippet.strip()
        ]

        # Build a concise, structured answer from the top evidence chunks.
        answer_lines: list[str] = []
        seen_snippets: set[str] = set()

        for idx, citation in enumerate(top, start=1):
            body = citation.snippet.strip() or citation.source_preview[:180].strip()
            if not body or body in seen_snippets:
                continue
            seen_snippets.add(body)
            # Label each claim with its source so users can verify it.
            section = f" — {citation.section_label}" if citation.section_label else ""
            answer_lines.append(
                f"[{idx}] {body} "
                f"(Source: {citation.document_title}{section}, chunk #{citation.chunk_id})"
            )

        if not answer_lines:
            answer_text = "No relevant evidence was found for this query in the indexed documents."
        else:
            answer_text = (
                "Based on the indexed knowledge base:\n\n"
                + "\n\n".join(answer_lines)
                + "\n\nVerify policy-sensitive details directly in the cited sources before acting."
            )

        return LLMGeneration(
            text=answer_text,
            mode="grounded_heuristic",
            evidence_summary=evidence_summary,
        )


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        provider = settings.llm_provider.lower()
        self.provider = HeuristicGroundedLLM() if provider == "heuristic" else HeuristicGroundedLLM()

    def generate_grounded_answer(self, query: str, citations: list[Citation]) -> LLMGeneration:
        return self.provider.generate(query=query, citations=citations)


llm_service = LLMService()
