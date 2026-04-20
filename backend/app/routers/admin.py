from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.admin import AdminAnalyticsSummaryResponse, AdminIngestionStatusResponse, AdminTopDocumentResponse
from app.services.admin_service import AdminService

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
