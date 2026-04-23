from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.admin import (
    AdminAnalyticsSummaryResponse,
    AdminUserResponse,
    BenchmarkRunResponse,
    CollectionSummaryResponse,
    FeedbackSummaryResponse,
    AdminIngestionStatusResponse,
    AdminTopDocumentResponse,
    AuditLogResponse,
    WorkspaceSettingsResponse,
    WorkspaceSettingsUpdateRequest,
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
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[AuditLogResponse]:
    service = AdminService(db)
    logs = service.get_audit_logs(user.organization_id, action=action, resource_type=resource_type)
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


@router.get("/workspace", response_model=WorkspaceSettingsResponse)
def get_workspace_settings(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> WorkspaceSettingsResponse:
    payload = AdminService(db).get_workspace_settings(user.organization_id)
    return WorkspaceSettingsResponse(**payload)


@router.put("/workspace", response_model=WorkspaceSettingsResponse)
def update_workspace_settings(
    payload: WorkspaceSettingsUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> WorkspaceSettingsResponse:
    service = AdminService(db)
    try:
        updated = service.update_workspace_name(user.organization_id, payload.organization_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return WorkspaceSettingsResponse(**updated)


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> list[AdminUserResponse]:
    users = AdminService(db).list_users(user.organization_id)
    return [AdminUserResponse.model_validate(item) for item in users]
