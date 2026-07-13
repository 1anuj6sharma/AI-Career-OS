"""
JWT Utilities

Responsible for:
- Creating Access Tokens
- Creating Refresh Tokens
- Decoding Tokens
- Validating Tokens
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings

# -------------------------------------------------------------------
# JWT Configuration
# -------------------------------------------------------------------

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# -------------------------------------------------------------------
# Create Access Token
# -------------------------------------------------------------------

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate JWT Access Token.
    """

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# -------------------------------------------------------------------
# Create Refresh Token
# -------------------------------------------------------------------

def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate JWT Refresh Token.
    """

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# -------------------------------------------------------------------
# Decode Token
# -------------------------------------------------------------------

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        raise ValueError("Invalid or expired token.")


# -------------------------------------------------------------------
# Token Type Helpers
# -------------------------------------------------------------------

def is_access_token(payload: Dict[str, Any]) -> bool:
    """
    Check if payload belongs to an access token.
    """
    return payload.get("type") == "access"


def is_refresh_token(payload: Dict[str, Any]) -> bool:
    """
    Check if payload belongs to a refresh token.
    """
    return payload.get("type") == "refresh"
