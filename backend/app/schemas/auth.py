from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    organization_id: int


class UserContext(BaseModel):
    user_id: int
    email: str
    role: str
    organization_id: int
