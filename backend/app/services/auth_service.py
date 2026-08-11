"""
Authentication Service
"""

from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService


class AuthService:

    def __init__(self, db: Session):

        self.repository = UserRepository(db)

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
    ):

        if self.repository.exists_by_email(email):

            raise ValueError("Email already registered.")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
        )

        user = self.repository.create(user)

        tokens = TokenService.generate_tokens(
            {
                "sub": str(user.id),
                "email": user.email,
            }
        )

        return user, tokens

    def login(
        self,
        email: str,
        password: str,
    ):

        user = self.repository.get_by_email(email)

        if not user:

            raise ValueError("Invalid credentials.")

        if not verify_password(
            password,
            user.password,
        ):

            raise ValueError("Invalid credentials.")

        return TokenService.generate_tokens(
            {
                "sub": str(user.id),
                "email": user.email,
            }
        )
