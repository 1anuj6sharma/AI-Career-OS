from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token, is_access_token, is_refresh_token
from app.core.config import settings
from app.core.exception import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidTokenException,
    TokenExpiredException,
    ValidationException,
    ForbiddenException,
)
from app.modules.auth.models import User, RefreshToken
from app.modules.auth.repository import UserRepository, RefreshTokenRepository
from app.modules.auth.validators import validate_password

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
    
    def register(self, first_name, last_name, email, password):
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            raise ValidationException(message)
        
        # Check duplicate
        if self.user_repo.exists_by_email(email):
            raise UserAlreadyExistsException()
        
        # Create user (transactional)
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(password),
        )
        user = self.user_repo.create(user)
        self.db.commit()
        
        return user
    
    def login(self, email, password):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise ForbiddenException()
        
        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        self.token_repo.create(db_token)
        self.db.commit()
        
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
        return user, tokens
    
    def refresh_token(self, refresh_token_str):
        # Decode the token
        try:
            payload = decode_token(refresh_token_str)
        except ValueError:
            raise InvalidTokenException()
        
        if not is_refresh_token(payload):
            raise InvalidTokenException()
        
        # Check if token exists and is not revoked
        db_token = self.token_repo.get_active_token(refresh_token_str)
        if not db_token:
            raise InvalidTokenException()
        
        # Check expiration
        if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise TokenExpiredException()
        
        # Get user
        user_id = int(payload.get("sub"))
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidTokenException()
        
        # Revoke old token (rotation)
        self.token_repo.revoke_token(refresh_token_str)
        
        # Generate new tokens
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Store new refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_db_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at,
        )
        self.token_repo.create(new_db_token)
        self.db.commit()
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    
    def logout(self, refresh_token_str):
        self.token_repo.revoke_token(refresh_token_str)
        self.db.commit()
    
    def get_current_user(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user
