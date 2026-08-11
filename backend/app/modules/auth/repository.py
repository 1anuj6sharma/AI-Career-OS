from sqlalchemy.orm import Session
from app.modules.auth.models import User, RefreshToken
from datetime import datetime, timezone
from typing import Optional, List

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def exists_by_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None
    
    def update(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        return user

class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)
        return token
    
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
    
    def get_active_token(self, token: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),
        ).first()
    
    def revoke_token(self, token: str) -> bool:
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return False
        refresh_token.is_revoked = True
        self.db.flush()
        return True
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        result = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        ).update({"is_revoked": True})
        self.db.flush()
        return result
