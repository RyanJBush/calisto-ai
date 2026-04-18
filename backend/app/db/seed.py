from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Organization, User


def seed_demo_data(db: Session) -> None:
    if db.query(User).first():
        return

    org = Organization(name="Calisto Demo Org")
    db.add(org)
    db.flush()

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
