from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class EntraLoginRequest(BaseModel):
    access_token: str = Field(..., description="MS Entra ID access token")
    job_title: str = Field(default="", description="jobTitle จาก Graph API (frontend ส่งมาเป็น fallback)")


class DraftLoginRequest(BaseModel):
    """Development/staging only — simulates Entra login using job_title string."""
    job_title: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    position: str | None = None
    coordinator: bool = False
    name: str


class UserInfo(BaseModel):
    username: str
    role: str
    position: str | None = None
    coordinator: bool = False
    expires_at: str | None = None
