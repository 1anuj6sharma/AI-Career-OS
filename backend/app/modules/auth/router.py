from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, TokenResponse,
    MessageResponse, UserResponse,
)
from app.modules.auth.service import AuthService
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED,
             summary="Register a new user", description="Create a new user account with email and password.")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password=request.password,
    )
    return RegisterResponse(message="User registered successfully.", user=UserResponse.model_validate(user))

@router.post("/login", response_model=LoginResponse,
             summary="Login", description="Authenticate with email and password to receive access and refresh tokens.")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user, tokens = service.login(email=request.email, password=request.password)
    return LoginResponse(user=UserResponse.model_validate(user), tokens=tokens)

@router.post("/refresh", response_model=TokenResponse,
             summary="Refresh token", description="Exchange a valid refresh token for a new access token and refresh token.")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_token(request.refresh_token)

@router.post("/logout", response_model=MessageResponse,
             summary="Logout", description="Revoke the provided refresh token.")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(request.refresh_token)
    return MessageResponse(message="Logged out successfully.")

@router.get("/me", response_model=UserResponse,
            summary="Get current user", description="Get the authenticated user's information.")
def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(current_user)
