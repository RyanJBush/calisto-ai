from dataclasses import dataclass

from app.config import get_settings
from app.schemas.chat import Citation


@dataclass
class LLMGeneration:
    text: str
    mode: str
    evidence_summary: list[str]


class HeuristicGroundedLLM:
    def generate(self, query: str, citations: list[Citation]) -> LLMGeneration:
        ordered = sorted(citations, key=lambda citation: citation.retrieval_score, reverse=True)
        top = ordered[:3]
        evidence_summary = [
            f"{citation.document_title}: {citation.snippet.strip()}" for citation in top if citation.snippet.strip()
        ]

        lines = [f"Grounded answer for: '{query}'"]
        for index, citation in enumerate(top, start=1):
            lines.append(f"- Evidence [{index}] from {citation.document_title}: {citation.snippet.strip()}")
        lines.append("Use the cited sources to verify policy-sensitive details before acting.")

        return LLMGeneration(
            text="\n".join(lines),
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
