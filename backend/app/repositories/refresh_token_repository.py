"""
Refresh Token Repository

Handles all database operations related to refresh tokens.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository for RefreshToken model.
    """

    def __init__(self, db: Session):
        super().__init__(RefreshToken, db)

    # ---------------------------------------------------------
    # Get by Token
    # ---------------------------------------------------------

    def get_by_token(
        self,
        token: str,
    ) -> Optional[RefreshToken]:

        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token == token)
            .first()
        )

    # ---------------------------------------------------------
    # Get Active Token
    # ---------------------------------------------------------

    def get_active_token(
        self,
        token: str,
    ) -> Optional[RefreshToken]:

        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.is_revoked.is_(False),
            )
            .first()
        )

    # ---------------------------------------------------------
    # Get User Tokens
    # ---------------------------------------------------------

    def get_user_tokens(
        self,
        user_id: int,
    ) -> List[RefreshToken]:

        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
            )
            .all()
        )

    # ---------------------------------------------------------
    # Revoke Token
    # ---------------------------------------------------------

    def revoke_token(
        self,
        token: str,
    ) -> bool:

        refresh_token = self.get_by_token(token)

        if not refresh_token:
            return False

        refresh_token.is_revoked = True

        self.db.commit()

        return True

    # ---------------------------------------------------------
    # Revoke All User Tokens
    # ---------------------------------------------------------

    def revoke_all_user_tokens(
        self,
        user_id: int,
    ) -> int:

        tokens = self.get_user_tokens(user_id)

        for token in tokens:
            token.is_revoked = True

        self.db.commit()

        return len(tokens)

    # ---------------------------------------------------------
    # Delete Expired Tokens
    # ---------------------------------------------------------

    def delete_expired_tokens(self) -> int:

        expired_tokens = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
            .all()
        )

        count = len(expired_tokens)

        for token in expired_tokens:
            self.db.delete(token)

        self.db.commit()

        return count

    # ---------------------------------------------------------
    # Exists
    # ---------------------------------------------------------

    def exists(
        self,
        token: str,
    ) -> bool:

        return self.get_by_token(token) is not None
