"""
Authentication Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    user, _ = service.register(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password=request.password,
    )

    return RegisterResponse(
        message="User registered successfully.",
        user=user,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    user, tokens = service.login(
        email=request.email,
        password=request.password,
    )

    return LoginResponse(
        user=user,
        tokens=tokens,
    )


@router.post(
    "/refresh",
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    return service.refresh_token(
        request.refresh_token,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    service.logout(
        request.refresh_token,
    )

    return LogoutResponse(
        message="Logged out successfully."
    )
