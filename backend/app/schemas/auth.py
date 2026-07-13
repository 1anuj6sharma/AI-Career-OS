"""
Authentication Schemas

Contains:
- User Registration
- User Login
- Token Responses
- Refresh Token
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -------------------------------------------------------------------
# Register
# -------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """
    Request schema for user registration.
    """

    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


# -------------------------------------------------------------------
# Login
# -------------------------------------------------------------------

class LoginRequest(BaseModel):
    """
    Request schema for login.
    """

    email: EmailStr
    password: str


# -------------------------------------------------------------------
# Refresh Token
# -------------------------------------------------------------------

class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing access token.
    """

    refresh_token: str


# -------------------------------------------------------------------
# Token Response
# -------------------------------------------------------------------

class TokenResponse(BaseModel):
    """
    Response returned after login.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# -------------------------------------------------------------------
# User Response
# -------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Public user information.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime


# -------------------------------------------------------------------
# Login Response
# -------------------------------------------------------------------

class LoginResponse(BaseModel):
    """
    Login response.
    """

    user: UserResponse
    tokens: TokenResponse


# -------------------------------------------------------------------
# Register Response
# -------------------------------------------------------------------

class RegisterResponse(BaseModel):
    """
    Registration response.
    """

    message: str
    user: UserResponse


# -------------------------------------------------------------------
# Logout Response
# -------------------------------------------------------------------

class LogoutResponse(BaseModel):
    """
    Logout response.
    """

    message: str
