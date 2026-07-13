"""
Security utilities.

Responsible for:

- Password hashing
- Password verification
- Password validation
"""

import re

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify password against stored hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def validate_password_strength(password: str) -> bool:
    """
    Password Policy

    Minimum 8 characters

    At least one uppercase

    At least one lowercase

    At least one digit

    At least one special character
    """

    pattern = (
        r"^(?=.*[a-z])"
        r"(?=.*[A-Z])"
        r"(?=.*\d)"
        r"(?=.*[@$!%*?&])"
        r"[A-Za-z\d@$!%*?&]{8,}$"
    )

    return bool(re.match(pattern, password))
