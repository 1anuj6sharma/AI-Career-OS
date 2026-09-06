"""
Connected Accounts persistence.

`UserIntegration` is the account record.  Imported platform data is stored in
NORMALIZED tables — `IntegrationMetric` (one numeric/text metric per row) and
`IntegrationArtifact` (one repository / model / dataset / notebook / solved
problem per row) — rather than in one large JSON blob, so the evidence can be
queried, joined and aggregated by the rest of the product.

`telemetry_summary` retains only the small sanitized summary the UI renders
(counts and the provider's own limitation note). Tokens are never stored in
plaintext: see `app/controllers/integrations/crypto.py`.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserIntegration(Base):
    """One connected external account for one user."""

    __tablename__ = "user_integrations"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_integration_provider"),
        Index("ix_user_integrations_status", "connection_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Fernet ciphertext only — never a plaintext credential (spec §5).
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # User-supplied official API token (e.g. Kaggle), same encryption.
    api_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scopes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    #: One of providers.base.ConnectionState.
    connection_status: Mapped[str] = mapped_column(String(50), default="NOT_CONNECTED", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    #: Small sanitized summary for the UI. Bulk data lives in the tables below.
    telemetry_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    last_connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_sync_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    #: User-safe message only. Technical detail goes to the server log.
    last_sync_error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)  # legacy column
    sync_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    metrics: Mapped[list["IntegrationMetric"]] = relationship(
        "IntegrationMetric",
        back_populates="integration",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    artifacts: Mapped[list["IntegrationArtifact"]] = relationship(
        "IntegrationArtifact",
        back_populates="integration",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sync_runs: Mapped[list["IntegrationSyncRun"]] = relationship(
        "IntegrationSyncRun",
        back_populates="integration",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class IntegrationMetric(Base):
    """
    One measured value from a provider (e.g. github.total_stars = 48).

    Normalized so Career Analytics can query metrics across providers without
    parsing JSON, and so a metric the provider did not return is simply absent
    rather than defaulted to zero.
    """

    __tablename__ = "integration_metrics"
    __table_args__ = (
        UniqueConstraint("integration_id", "metric_key", name="uq_integration_metric_key"),
        Index("ix_integration_metrics_user_key", "user_id", "metric_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    integration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_integrations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    metric_key: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metric_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    integration: Mapped["UserIntegration"] = relationship("UserIntegration", back_populates="metrics")


class IntegrationArtifact(Base):
    """
    One piece of concrete career evidence imported from a provider: a
    repository, a Hugging Face model, a Kaggle dataset or notebook, a solved
    LeetCode problem, a classified job email.
    """

    __tablename__ = "integration_artifacts"
    __table_args__ = (
        UniqueConstraint(
            "integration_id", "artifact_type", "external_id", name="uq_integration_artifact_external"
        ),
        Index("ix_integration_artifacts_user_type", "user_id", "artifact_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    integration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_integrations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    #: repository | model | dataset | space | notebook | problem | job_email
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    primary_language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    stars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    forks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    downloads: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    #: Small per-artifact extras only (tags, difficulty) — not a state dump.
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    integration: Mapped["UserIntegration"] = relationship("UserIntegration", back_populates="artifacts")


class IntegrationSyncRun(Base):
    """Audit trail for every sync attempt — real timestamps, real outcomes."""

    __tablename__ = "integration_sync_runs"
    __table_args__ = (Index("ix_integration_sync_runs_started", "integration_id", "started_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    integration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_integrations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)

    #: manual | initial | scheduled
    trigger: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    #: SYNCED | SYNC_FAILED | REAUTH_REQUIRED | SKIPPED
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    metrics_written: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    artifacts_written: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evidence_written: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    integration: Mapped["UserIntegration"] = relationship("UserIntegration", back_populates="sync_runs")


class OAuthAuthorizationState(Base):
    """
    Server-side CSRF state and PKCE verifier for an in-flight OAuth flow.

    Persisted (not in-process) so state survives a restart and multiple workers,
    single-use via `consumed_at`, and expiring via `expires_at` (spec §5).
    The PKCE verifier is stored encrypted — it is a short-lived secret.
    """

    __tablename__ = "oauth_authorization_states"
    __table_args__ = (Index("ix_oauth_states_expiry", "expires_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    #: Opaque random value echoed by the provider.
    state: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    code_verifier_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    redirect_uri: Mapped[str] = mapped_column(String(512), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
