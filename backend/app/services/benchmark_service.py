from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.retrieval_service import RetrievalService


@dataclass
class BenchmarkCase:
    question: str
    expected_terms: list[str]


class BenchmarkService:
    SAMPLE_CASES = [
        BenchmarkCase(
            question="What does Calisto AI provide for answer trust?",
            expected_terms=["citation", "grounded", "source"],
        ),
        BenchmarkCase(
            question="How does document ingestion work?",
            expected_terms=["ingestion", "chunk", "embedding"],
        ),
    ]

    def __init__(self, db: Session) -> None:
        self.retrieval_service = RetrievalService(db)

    def run(self, organization_id: int) -> dict[str, float | int]:
        total = len(self.SAMPLE_CASES)
        passed = 0
        aggregate_score = 0.0
        for case in self.SAMPLE_CASES:
            results = self.retrieval_service.retrieve(case.question, organization_id=organization_id, top_k=3)
            content_blob = " ".join(chunk.content.lower() for chunk, _score in results)
            covered = sum(1 for term in case.expected_terms if term in content_blob)
            case_score = covered / max(1, len(case.expected_terms))
            aggregate_score += case_score
            if case_score >= 0.5:
                passed += 1

        average_score = aggregate_score / max(1, total)
        return {
            "cases_total": total,
            "cases_passed": passed,
            "pass_rate": round(passed / max(1, total), 4),
            "average_case_score": round(average_score, 4),
        }
