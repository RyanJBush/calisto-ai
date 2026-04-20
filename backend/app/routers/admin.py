from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.admin import AdminAnalyticsSummaryResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/analytics/summary", response_model=AdminAnalyticsSummaryResponse)
def analytics_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> AdminAnalyticsSummaryResponse:
    service = AdminService(db)
    return AdminAnalyticsSummaryResponse(**service.get_analytics_summary(user.organization_id))
