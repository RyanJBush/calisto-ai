from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.admin import (
    AdminAnalyticsSummaryResponse,
    BenchmarkRunResponse,
    CollectionSummaryResponse,
    FeedbackSummaryResponse,
    AdminIngestionStatusResponse,
    AdminTopDocumentResponse,
    AuditLogResponse,
)
from app.services.admin_service import AdminService
from app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/analytics/summary", response_model=AdminAnalyticsSummaryResponse)
def analytics_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> AdminAnalyticsSummaryResponse:
    service = AdminService(db)
    return AdminAnalyticsSummaryResponse(**service.get_analytics_summary(user.organization_id))


@router.get("/analytics/top-documents", response_model=list[AdminTopDocumentResponse])
def analytics_top_documents(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[AdminTopDocumentResponse]:
    service = AdminService(db)
    payload = service.get_top_documents_by_chunk_count(user.organization_id)
    return [AdminTopDocumentResponse(**item) for item in payload]


@router.get("/analytics/ingestion-breakdown", response_model=list[AdminIngestionStatusResponse])
def analytics_ingestion_breakdown(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[AdminIngestionStatusResponse]:
    service = AdminService(db)
    payload = service.get_ingestion_status_breakdown(user.organization_id)
    return [AdminIngestionStatusResponse(**item) for item in payload]


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def audit_logs(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[AuditLogResponse]:
    service = AdminService(db)
    logs = service.get_audit_logs(user.organization_id)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/analytics/feedback-summary", response_model=FeedbackSummaryResponse)
def feedback_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> FeedbackSummaryResponse:
    service = AdminService(db)
    return FeedbackSummaryResponse(**service.get_feedback_summary(user.organization_id))


@router.get("/analytics/benchmark", response_model=BenchmarkRunResponse)
def benchmark(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> BenchmarkRunResponse:
    service = BenchmarkService(db)
    return BenchmarkRunResponse(**service.run(user.organization_id))


@router.get("/analytics/collections", response_model=list[CollectionSummaryResponse])
def collection_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[CollectionSummaryResponse]:
    service = AdminService(db)
    payload = service.get_collection_summary(user.organization_id)
    return [CollectionSummaryResponse(**item) for item in payload]
