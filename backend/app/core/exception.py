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

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(CareerOSException)
    async def career_os_exception_handler(request: Request, exc: CareerOSException):
        status_code = status.HTTP_400_BAD_REQUEST
        
        if isinstance(exc, InvalidCredentialsException):
            status_code = status.HTTP_401_UNAUTHORIZED
            error_code = "INVALID_CREDENTIALS"
        elif isinstance(exc, UnauthorizedException):
            status_code = status.HTTP_401_UNAUTHORIZED
            error_code = "UNAUTHORIZED"
        elif isinstance(exc, ForbiddenException):
            status_code = status.HTTP_403_FORBIDDEN
            error_code = "FORBIDDEN"
        elif isinstance(exc, TokenExpiredException):
            status_code = status.HTTP_401_UNAUTHORIZED
            error_code = "TOKEN_EXPIRED"
        elif isinstance(exc, InvalidTokenException):
            status_code = status.HTTP_401_UNAUTHORIZED
            error_code = "INVALID_TOKEN"
        elif isinstance(exc, UserAlreadyExistsException):
            status_code = status.HTTP_409_CONFLICT
            error_code = "USER_ALREADY_EXISTS"
        elif isinstance(exc, UserNotFoundException):
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "USER_NOT_FOUND"
        elif isinstance(exc, ValidationException):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_code = "VALIDATION_ERROR"
        elif isinstance(exc, ResourceNotFoundException):
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "RESOURCE_NOT_FOUND"
        elif isinstance(exc, DuplicateResourceException):
            status_code = status.HTTP_409_CONFLICT
            error_code = "DUPLICATE_RESOURCE"
        else:
            error_code = "BAD_REQUEST"

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": exc.message
                }
            }
        )
