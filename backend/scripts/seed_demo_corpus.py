from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User
from app.services.document_service import DocumentService

DEMO_DOCUMENTS = [
    {
        "title": "Security Handbook",
        "source_name": "security-handbook.md",
        "content": (
            "Calisto AI requires role-based access control for admin, member, and viewer personas. "
            "All production deployments must configure a non-default JWT secret and review audit logs weekly."
        ),
    },
    {
        "title": "Product FAQ",
        "source_name": "product-faq.md",
        "content": (
            "Calisto AI supports citation-aware responses. "
            "Users should verify answers using source previews and confidence indicators in chat."
        ),
    },
    {
        "title": "Ingestion Operations",
        "source_name": "ingestion-ops.md",
        "content": (
            "Document ingestion supports text and PDF uploads. "
            "Failed ingestions can be retried from the documents page or via API retry endpoint."
        ),
    },
]


def seed_demo_corpus(db: Session) -> int:
    user = db.query(User).filter(User.email == "member@calisto.ai").first()
    if user is None:
        raise RuntimeError("Expected seeded member user is missing. Run make init first.")

    service = DocumentService(db)
    seeded = 0
    for document in DEMO_DOCUMENTS:
        try:
            service.upload_document_content(
                title=document["title"],
                content=document["content"],
                source_name=document["source_name"],
                redact_pii=False,
                collection_id=None,
                user=user,
            )
            seeded += 1
        except ValueError:
            continue
    return seeded


def main() -> None:
    db = SessionLocal()
    try:
        seeded = seed_demo_corpus(db)
        print(f"Seeded {seeded} demo documents.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
