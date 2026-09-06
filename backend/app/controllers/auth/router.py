from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.views.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, TokenResponse,
    MessageResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
    VerifyEmailRequest, RecoveryResponse, TokenCheckResponse,
)
from app.controllers.auth.account_recovery import AccountRecoveryService
from app.controllers.auth.service import AuthService
from app.controllers.auth.dependencies import get_current_active_user
from app.models.auth import User

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
    # Send the verification link now, and report honestly if mail is unavailable
    # instead of telling the user to check an inbox that will stay empty.
    verification = AccountRecoveryService(db).send_verification_email(user)
    message = (
        "Account created. Check your inbox to verify your email address."
        if verification.email_delivered
        else "Account created. We could not send the verification email yet — "
             "you can request it again from your profile."
    )
    return RegisterResponse(message=message, user=UserResponse.model_validate(user))

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


# ---------------------------------------------------------------------------
# Account recovery
# ---------------------------------------------------------------------------

def _client_ip(request: Request) -> str | None:
    """Left-most X-Forwarded-For entry when behind a proxy, else the peer."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return request.client.host if request.client else None


def _recovery_response(outcome) -> RecoveryResponse:
    """
    Only expose the dev outbox path in DEBUG — it is a filesystem path and a
    live reset link, so it must never appear in a production response.
    """
    return RecoveryResponse(
        message=outcome.message,
        email_delivered=outcome.email_delivered,
        email_outbox_path=outcome.email_outbox_path if settings.DEBUG else None,
    )


@router.post(
    "/forgot-password",
    response_model=RecoveryResponse,
    summary="Request a password reset email",
    description=(
        "Sends a single-use, expiring reset link. The response is identical "
        "whether or not the address is registered, so it cannot be used to "
        "discover accounts."
    ),
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    outcome = AccountRecoveryService(db).request_password_reset(
        payload.email,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return _recovery_response(outcome)


@router.get(
    "/reset-password/validate",
    response_model=TokenCheckResponse,
    summary="Check whether a reset token is still usable",
)
def validate_reset_token(token: str, db: Session = Depends(get_db)):
    return TokenCheckResponse(valid=AccountRecoveryService(db).validate_reset_token(token))


@router.post(
    "/reset-password",
    response_model=RecoveryResponse,
    summary="Set a new password using a reset token",
    description="Consumes the token, applies the password policy, and signs out every other session.",
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    outcome = AccountRecoveryService(db).reset_password(payload.token, payload.new_password)
    return _recovery_response(outcome)


@router.post(
    "/send-verification",
    response_model=RecoveryResponse,
    summary="Send (or resend) the email verification link",
)
def send_verification(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    outcome = AccountRecoveryService(db).send_verification_email(current_user)
    return _recovery_response(outcome)


@router.post(
    "/verify-email",
    response_model=RecoveryResponse,
    summary="Confirm an email address using a verification token",
)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    _, outcome = AccountRecoveryService(db).verify_email(payload.token)
    return _recovery_response(outcome)
