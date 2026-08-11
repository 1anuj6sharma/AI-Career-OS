"""
User Service
"""

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, db: Session):

        self.repository = UserRepository(db)

    def get_user(self, user_id: int):

        return self.repository.get(user_id)

    def update_user(self, user):

        return self.repository.update(user)

    def delete_user(self, user):

        return self.repository.delete(user)
