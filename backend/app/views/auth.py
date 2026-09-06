from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Account recovery (password reset / email verification)
# ---------------------------------------------------------------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=16, max_length=512)
    new_password: str = Field(..., min_length=8, max_length=200)


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=16, max_length=512)


class RecoveryResponse(BaseModel):
    """
    `message` is what the user sees. `email_delivered` is the truth about
    delivery — it is False when SMTP is unconfigured or the send failed, so the
    UI never claims an email was sent when it was not.
    """

    message: str
    email_delivered: bool = False
    #: Development only: where the message was written when SMTP is absent.
    email_outbox_path: str | None = None


class TokenCheckResponse(BaseModel):
    valid: bool
