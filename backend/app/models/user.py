import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class Role(str, enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.viewer, nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)

    organization = relationship("Organization", back_populates="users")
    documents = relationship("Document", back_populates="uploaded_by")
