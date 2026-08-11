"""
User Repository
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(
    BaseRepository[User]
):

    def __init__(
        self,
        db: Session,
    ):

        super().__init__(
            User,
            db,
        )

    # -----------------------------------------------------

    def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    # -----------------------------------------------------

    def get_by_username(
        self,
        username: str,
    ) -> Optional[User]:

        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    # -----------------------------------------------------

    def exists_by_email(
        self,
        email: str,
    ) -> bool:

        return (
            self.get_by_email(email)
            is not None
        )
