from sqlalchemy.orm import Session

from app.models import AuditLog, User


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        organization_id: int,
        action: str,
        resource_type: str,
        resource_id: int | None = None,
        details: str | None = None,
        user: User | None = None,
        commit: bool = False,
    ) -> None:
        self.db.add(
            AuditLog(
                organization_id=organization_id,
                user_id=user.id if user else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
            )
        )
        if commit:
            self.db.commit()
