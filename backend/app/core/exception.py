"""
Custom application exceptions.

These exceptions are raised throughout the application
and later handled by a global exception handler.
"""




class CareerOSException(Exception):
    """
    Base exception for the application.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# ============================
# Authentication Exceptions
# ============================

class InvalidCredentialsException(CareerOSException):
    def __init__(self):
        super().__init__("Invalid email or password.")


class UnauthorizedException(CareerOSException):
    def __init__(self):
        super().__init__("You are not authorized to perform this action.")


class ForbiddenException(CareerOSException):
    def __init__(self):
        super().__init__("Access forbidden.")


class TokenExpiredException(CareerOSException):
    def __init__(self):
        super().__init__("Authentication token has expired.")


class InvalidTokenException(CareerOSException):
    def __init__(self):
        super().__init__("Invalid authentication token.")


# ============================
# User Exceptions
# ============================

class UserAlreadyExistsException(CareerOSException):
    def __init__(self):
        super().__init__("User already exists.")


class UserNotFoundException(CareerOSException):
    def __init__(self):
        super().__init__("User not found.")


# ============================
# Validation Exceptions
# ============================

class ValidationException(CareerOSException):
    def __init__(self, message: str):
        super().__init__(message)


# ============================
# Database Exceptions
# ============================

class DatabaseException(CareerOSException):
    def __init__(self):
        super().__init__("Database operation failed.")


# ============================
# Resource Exceptions
# ============================

class ResourceNotFoundException(CareerOSException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found.")


class DuplicateResourceException(CareerOSException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} already exists.")
        
from jose import JWTError, jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload

    except JWTError as exc:
        raise AuthenticationException(
            detail="Invalid or expired token."
        ) from exc
