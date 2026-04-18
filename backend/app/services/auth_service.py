from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, verify_password
from app.models import User


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def authenticate(self, email: str, password: str) -> str | None:
        user = self.db.query(User).filter(User.email == email).first()
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return create_access_token(str(user.id))

    def get_user_from_token(self, token: str) -> User | None:
        try:
            user_id = int(decode_access_token(token))
        except (ValueError, TypeError):
            return None
        return self.db.get(User, user_id)
