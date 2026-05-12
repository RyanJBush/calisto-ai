import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models import Chunk, Document, IngestionRun
from app.services.embedding_index_service import embedding_index_service
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.security_text_service import SecurityTextService


class IngestionJobService:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="calisto-ingestion")

    def enqueue(self, document_id: int, ingestion_run_id: int) -> None:
        self.executor.submit(self._ingest_document, document_id, ingestion_run_id)

    def _ingest_document(self, document_id: int, ingestion_run_id: int) -> None:
        db = SessionLocal()
        ingestion_service = IngestionService()
        embedding_service = EmbeddingService()
        security_text_service = SecurityTextService()

        max_attempts = 3
        try:
            for attempt in range(1, max_attempts + 1):
                ingestion_run = db.get(IngestionRun, ingestion_run_id)
                document = db.get(Document, document_id)
                if ingestion_run is None or document is None:
                    return

                ingestion_run.status = "processing"
                ingestion_run.attempts = attempt
                ingestion_run.error_message = None
                ingestion_run.started_at = datetime.now(timezone.utc)
                ingestion_run.completed_at = None
                db.commit()

                try:
                    existing_chunk_ids = [row.id for row in db.query(Chunk.id).filter(Chunk.document_id == document_id).all()]
                    embedding_index_service.delete_embeddings_for_chunk_ids(db, existing_chunk_ids)
                    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
                    db.commit()

                    safe_content = security_text_service.sanitize_prompt_injection(document.content)
                    document.content = safe_content
                    chunks = ingestion_service.chunk_document(document)
                    for chunk in chunks:
                        db.add(chunk)
                    db.flush()

                    for chunk in chunks:
                        embedding_index_service.upsert_chunk_embedding(
                            db,
                            chunk.id,
                            embedding_service.embed_text(chunk.content),
                        )
                    db.commit()

                    ingestion_run.status = "completed"
                    ingestion_run.completed_at = datetime.now(timezone.utc)
                    ingestion_run.error_message = None
                    db.commit()
                    return
                except Exception as exc:  # noqa: PERF203
                    db.rollback()
                    ingestion_run = db.get(IngestionRun, ingestion_run_id)
                    if ingestion_run is None:
                        return
                    ingestion_run.error_message = str(exc)[:500]
                    ingestion_run.completed_at = datetime.now(timezone.utc)
                    ingestion_run.status = "failed" if attempt == max_attempts else "processing"
                    db.commit()
                    if attempt < max_attempts:
                        time.sleep(2 ** (attempt - 1))
        finally:
            db.close()


ingestion_job_service = IngestionJobService()
