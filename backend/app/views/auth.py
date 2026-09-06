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
