from sqlalchemy.orm import Session
import hashlib

from app.core.security import get_password_hash
from app.models import Chunk, Document, IngestionRun, Organization, User
from app.services.embedding_index_service import embedding_index_service
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService


def seed_demo_data(db: Session) -> None:
    org = db.query(Organization).filter(Organization.name == "Calisto Demo Org").first()
    if org is None:
        org = Organization(name="Calisto Demo Org")
        db.add(org)
        db.flush()

    users = db.query(User).filter(User.organization_id == org.id).all()
    if not users:
        users = [
            User(
                organization_id=org.id,
                email="admin@calisto.ai",
                full_name="Admin User",
                role="admin",
                password_hash=get_password_hash("password123"),
            ),
            User(
                organization_id=org.id,
                email="member@calisto.ai",
                full_name="Member User",
                role="member",
                password_hash=get_password_hash("password123"),
            ),
            User(
                organization_id=org.id,
                email="viewer@calisto.ai",
                full_name="Viewer User",
                role="viewer",
                password_hash=get_password_hash("password123"),
            ),
        ]
        db.add_all(users)
        db.commit()

    if db.query(Document).first():
        return

    ingestion_service = IngestionService()
    embedding_service = EmbeddingService()
    demo_docs = [
        (
            "Employee Handbook",
            "hr-handbook.md",
            "# Leave Policy\nEmployees receive 20 paid leave days yearly.\n\n# Remote Work\nManagers approve remote schedules quarterly.",
        ),
        (
            "Security Operations Guide",
            "security-guide.txt",
            "Incident severity levels are P1 to P4. P1 incidents require escalation within 15 minutes.",
        ),
        (
            "Support SLA",
            "support-sla.txt",
            "Enterprise support response SLA is 1 hour for critical issues and 8 hours for standard tickets.",
        ),
    ]
    for title, source_name, content in demo_docs:
        doc = Document(
            organization_id=org.id,
            uploaded_by=users[0].id,
            title=title,
            source_name=source_name,
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            version=1,
            content=content,
        )
        db.add(doc)
        db.flush()
        run = IngestionRun(document_id=doc.id, status="completed", attempts=1)
        db.add(run)
        chunks = ingestion_service.chunk_document(doc)
        for chunk in chunks:
            db.add(chunk)
        db.flush()
        for chunk in chunks:
            embedding_index_service.upsert_chunk_embedding(db, chunk.id, embedding_service.embed_text(chunk.content))
    db.commit()

    if db.query(Document).first():
        return

    ingestion_service = IngestionService()
    embedding_service = EmbeddingService()
    demo_docs = [
        (
            "Employee Handbook",
            "hr-handbook.md",
            "# Leave Policy\nEmployees receive 20 paid leave days yearly.\n\n# Remote Work\nManagers approve remote schedules quarterly.",
        ),
        (
            "Security Operations Guide",
            "security-guide.txt",
            "Incident severity levels are P1 to P4. P1 incidents require escalation within 15 minutes.",
        ),
        (
            "Support SLA",
            "support-sla.txt",
            "Enterprise support response SLA is 1 hour for critical issues and 8 hours for standard tickets.",
        ),
    ]
    for title, source_name, content in demo_docs:
        doc = Document(
            organization_id=org.id,
            uploaded_by=users[0].id,
            title=title,
            source_name=source_name,
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            version=1,
            content=content,
        )
        db.add(doc)
        db.flush()
        run = IngestionRun(document_id=doc.id, status="completed", attempts=1)
        db.add(run)
        chunks = ingestion_service.chunk_document(doc)
        for chunk in chunks:
            db.add(chunk)
        db.flush()
        for chunk in chunks:
            embedding_index_service.upsert_chunk_embedding(db, chunk.id, embedding_service.embed_text(chunk.content))
    db.commit()
