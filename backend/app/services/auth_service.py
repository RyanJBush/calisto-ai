from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import Organization
from app.models.user import Role, User

DEMO_USERS = [
    {
        "email": "admin@calisto.ai",
        "full_name": "Calisto Admin",
        "password": "admin1234",
        "role": Role.admin,
    },
    {
        "email": "member@calisto.ai",
        "full_name": "Calisto Member",
        "password": "member1234",
        "role": Role.member,
    },
    {
        "email": "viewer@calisto.ai",
        "full_name": "Calisto Viewer",
        "password": "viewer1234",
        "role": Role.viewer,
    },
]


def ensure_demo_seed_data(db: Session) -> None:
    organization = db.query(Organization).filter(Organization.name == "Calisto Demo Org").first()
    if not organization:
        organization = Organization(name="Calisto Demo Org")
        db.add(organization)
        db.flush()

    for seed in DEMO_USERS:
        existing = db.query(User).filter(User.email == seed["email"]).first()
        if existing:
            continue
        user = User(
            email=seed["email"],
            full_name=seed["full_name"],
            hashed_password=hash_password(seed["password"]),
            role=seed["role"],
            organization_id=organization.id,
        )
        db.add(user)
    db.commit()


def authenticate_and_issue_token(db: Session, email: str, password: str) -> tuple[str, User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    token = create_access_token(
        subject=user.email,
        role=user.role.value,
        organization_id=user.organization_id,
        user_id=user.id,
    )
    return token, user
