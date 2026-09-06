"""
Schemas for the Connected Accounts API.

Every model here is an *outbound* contract, and none of them carries a token,
refresh token, API secret or raw provider payload — the service builds these
from sanitized values only (spec §23, §27).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------- inbound

class IntegrationLinkIn(BaseModel):
    """
    Connect a platform that has no OAuth (public profile or link-only).

    There is deliberately no password field: we never ask for a third-party
    account password (spec §11, §12, §13).  `api_token` is accepted only by
    connectors that advertise `supports_api_token` — currently Kaggle's own
    API token — and is encrypted at rest.
    """

    identifier: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Public profile URL or username on the platform",
        examples=["torvalds", "https://leetcode.com/u/torvalds/"],
    )
    api_token: Optional[str] = Field(
        None,
        max_length=500,
        description=(
            "Optional official API token for platforms that offer one. "
            "Never a platform password."
        ),
    )


class IntegrationSyncIn(BaseModel):
    force: bool = Field(
        False, description="Bypass the minimum interval between manual syncs"
    )


class IntegrationDisconnectIn(BaseModel):
    purge_evidence: bool = Field(
        False,
        description=(
            "Also delete imported career evidence (repositories, models, solved "
            "problems). Off by default so career history survives a disconnect."
        ),
    )


# -------------------------------------------------------------------- outbound

class ProviderCapabilityOut(BaseModel):
    """Static provider metadata: what a platform can do on this deployment."""

    provider: str
    display_name: str
    auth_method: str
    capabilities: List[str] = []
    scopes: List[str] = []
    configured: bool
    missing_configuration: List[str] = []
    limitation_note: Optional[str] = None
    docs_url: Optional[str] = None
    supports_sync: bool
    supports_api_token: bool = False
    api_token_label: Optional[str] = None
    api_token_help: Optional[str] = None
    default_state: str


class ConnectedAccountOut(BaseModel):
    """One provider card: honest state plus only data we actually hold."""

    provider: str
    display_name: str
    auth_method: str
    connected: bool
    status: str = Field(
        ...,
        description=(
            "NOT_CONNECTED | CONNECTING | CONNECTED | SYNCING | SYNCED | "
            "SYNC_FAILED | REAUTH_REQUIRED | LIMITED | CONFIGURATION_REQUIRED | "
            "NOT_SUPPORTED"
        ),
    )
    capabilities: List[str] = []
    supports_sync: bool
    supports_api_token: bool = False
    api_token_label: Optional[str] = None
    api_token_help: Optional[str] = None
    configured: bool
    missing_configuration: List[str] = []
    limitation_note: Optional[str] = None
    docs_url: Optional[str] = None

    username: Optional[str] = None
    display_label: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    #: Validated https link to the official profile, for the [Open] button.
    external_url: Optional[str] = None
    scopes: List[str] = []

    last_connected_at: Optional[str] = None
    last_synced_at: Optional[str] = None
    last_sync_status: Optional[str] = None
    #: User-safe message only. Technical detail stays in server logs.
    last_sync_error: Optional[str] = None

    summary: Dict[str, Any] = {}
    artifact_counts: Dict[str, int] = {}


class IntegrationsOverviewOut(BaseModel):
    total_providers: int
    total_connected: int
    accounts: List[ConnectedAccountOut] = []
    #: Same accounts keyed by provider, for direct lookup in the UI.
    platforms: Dict[str, ConnectedAccountOut] = {}


class AuthorizationUrlOut(BaseModel):
    provider: str
    authorization_url: str
    #: Kept as `url` too because the existing frontend reads that key.
    url: str
    expires_in_seconds: int


class SyncErrorOut(BaseModel):
    code: str
    message: str


class SyncResultOut(BaseModel):
    provider: str
    status: str
    last_synced_at: Optional[str] = None
    metrics_written: int = 0
    artifacts_written: int = 0
    skills_written: int = 0
    pipeline: Dict[str, int] = {}
    summary: Dict[str, Any] = {}
    error: Optional[SyncErrorOut] = None
    retryable: bool = False
    requires_reauth: bool = False
    skipped: bool = False
    reason: Optional[str] = None


class DisconnectResultOut(BaseModel):
    provider: str
    status: str
    token_revoked_at_provider: bool
    removed: Dict[str, int] = {}
    evidence_retained: bool


class HealthOut(BaseModel):
    provider: str
    #: None when the provider offers nothing we can legitimately probe.
    reachable: Optional[bool] = None
    status_code: Optional[int] = None
    configured: bool
    missing_configuration: List[str] = []
    connection_status: str
    last_synced_at: Optional[str] = None
    token_expires_at: Optional[str] = None
    checked_at: str
    limitation_note: Optional[str] = None
    detail: Optional[str] = None


class IntegrationItemOut(BaseModel):
    """Legacy row shape, retained for callers that still read it."""

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
    last_synced_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    created_at: Optional[datetime] = None
