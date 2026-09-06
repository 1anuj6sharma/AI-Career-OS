from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class IntegrationConnectIn(BaseModel):
    platform: str = Field(..., example="github", description="Platform identifier: github, linkedin, leetcode, gfg, email, kaggle")
    identifier: str = Field(..., example="torvalds", description="Username, handle, profile URL or email address")
    access_token: Optional[str] = Field(None, description="Optional API key, personal access token or password")


class IntegrationLinkIn(BaseModel):
    identifier: str = Field(..., description="Public profile URL or username")

class IntegrationItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    provider: str
    provider_account_id: Optional[str] = None
    provider_username: Optional[str] = None
    display_name: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    connection_status: str
    is_active: bool
    telemetry_data: Dict[str, Any] = {}
    last_synced_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    created_at: Optional[datetime] = None


class IntegrationsStatusSummaryOut(BaseModel):
    total_connected: int
    platforms: Dict[str, Dict[str, Any]]
