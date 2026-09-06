from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserIntegration(Base):
    """
    Stores connected developer platforms (GitHub, LinkedIn, LeetCode, GFG, Email, Kaggle, HuggingFace)
    and their synchronized telemetry per user.
    """
    __tablename__ = "user_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # github, linkedin, leetcode, etc.
    provider_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scopes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    connection_status: Mapped[str] = mapped_column(String(50), default="NOT_CONNECTED")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    telemetry_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_sync_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
