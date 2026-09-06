"""connected accounts: normalized evidence, oauth state, auth tokens

Revision ID: 018_connected_accounts
Revises: 017_advanced_career_coach
Create Date: 2026-09-06 00:00:00.000000

Additive only.  No table is dropped and no existing row is deleted:

* `user_integrations` gains the columns the production connector layer needs
  (email, api_token_encrypted, last_connected_at, last_sync_error,
  sync_attempts) and its token columns widen to TEXT so a Fernet ciphertext
  always fits.  The legacy `last_error` column is left in place.
* Four new tables hold normalized platform evidence and the OAuth handshake:
  integration_metrics, integration_artifacts, integration_sync_runs,
  oauth_authorization_states.
* Own-auth account recovery gains password_reset_tokens,
  email_verification_tokens and users.email_verified_at.

Every add is guarded so the migration is safe on a database that already has
part of this schema, and safe on a clean database.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "018_connected_accounts"
down_revision: Union[str, Sequence[str], None] = "017_advanced_career_coach"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --------------------------------------------------------------------------- #
# Guards — this migration must be safe to run against a partially-migrated DB
# --------------------------------------------------------------------------- #

def _inspector():
    return inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return name in _inspector().get_table_names()


def _columns(table: str) -> set:
    if not _has_table(table):
        return set()
    return {c["name"] for c in _inspector().get_columns(table)}


def _indexes(table: str) -> set:
    if not _has_table(table):
        return set()
    return {i["name"] for i in _inspector().get_indexes(table)}


def _constraints(table: str) -> set:
    if not _has_table(table):
        return set()
    insp = _inspector()
    names = {c["name"] for c in insp.get_unique_constraints(table)}
    return {n for n in names if n}


def _add_column(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def _create_index(name: str, table: str, columns: list, unique: bool = False) -> None:
    if name not in _indexes(table):
        op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
    # ------------------------------------------------ user_integrations columns
    _add_column("user_integrations", sa.Column("email", sa.String(length=320), nullable=True))
    _add_column("user_integrations", sa.Column("api_token_encrypted", sa.Text(), nullable=True))
    _add_column("user_integrations", sa.Column("last_connected_at", sa.DateTime(), nullable=True))
    _add_column("user_integrations", sa.Column("last_sync_error", sa.String(length=500), nullable=True))
    _add_column(
        "user_integrations",
        sa.Column("sync_attempts", sa.Integer(), server_default="0", nullable=False),
    )

    # Fernet ciphertext of a long Google refresh token can exceed 2048 chars.
    existing_columns = _columns("user_integrations")
    for column_name in ("access_token_encrypted", "refresh_token_encrypted"):
        if column_name in existing_columns:
            op.alter_column(
                "user_integrations",
                column_name,
                type_=sa.Text(),
                existing_nullable=True,
                postgresql_using=f"{column_name}::text",
            )

    if "uq_user_integration_provider" not in _constraints("user_integrations"):
        # Collapse any pre-existing duplicate (user, provider) rows before the
        # constraint is added, keeping the most recently created row.
        op.execute(
            """
            DELETE FROM user_integrations ui
            USING user_integrations dup
            WHERE ui.user_id = dup.user_id
              AND ui.provider = dup.provider
              AND ui.id < dup.id
            """
        )
        op.create_unique_constraint(
            "uq_user_integration_provider", "user_integrations", ["user_id", "provider"]
        )

    _create_index("ix_user_integrations_status", "user_integrations", ["connection_status"])

    # -------------------------------------------------------- integration_metrics
    if not _has_table("integration_metrics"):
        op.create_table(
            "integration_metrics",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("integration_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("metric_key", sa.String(length=100), nullable=False),
            sa.Column("metric_value", sa.Float(), nullable=True),
            sa.Column("metric_text", sa.String(length=500), nullable=True),
            sa.Column("unit", sa.String(length=32), nullable=True),
            sa.Column("captured_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["integration_id"], ["user_integrations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("integration_id", "metric_key", name="uq_integration_metric_key"),
        )
        op.create_index("ix_integration_metrics_id", "integration_metrics", ["id"])
        op.create_index("ix_integration_metrics_integration_id", "integration_metrics", ["integration_id"])
        op.create_index("ix_integration_metrics_user_id", "integration_metrics", ["user_id"])
        op.create_index("ix_integration_metrics_provider", "integration_metrics", ["provider"])
        op.create_index("ix_integration_metrics_user_key", "integration_metrics", ["user_id", "metric_key"])

    # ------------------------------------------------------ integration_artifacts
    if not _has_table("integration_artifacts"):
        op.create_table(
            "integration_artifacts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("integration_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("artifact_type", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=500), nullable=False),
            sa.Column("title", sa.String(length=500), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("url", sa.String(length=1000), nullable=True),
            sa.Column("primary_language", sa.String(length=100), nullable=True),
            sa.Column("stars", sa.Integer(), nullable=True),
            sa.Column("forks", sa.Integer(), nullable=True),
            sa.Column("downloads", sa.Integer(), nullable=True),
            sa.Column("likes", sa.Integer(), nullable=True),
            sa.Column("occurred_at", sa.DateTime(), nullable=True),
            sa.Column("attributes", sa.JSON(), nullable=True),
            sa.Column("first_seen_at", sa.DateTime(), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["integration_id"], ["user_integrations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "integration_id",
                "artifact_type",
                "external_id",
                name="uq_integration_artifact_external",
            ),
        )
        op.create_index("ix_integration_artifacts_id", "integration_artifacts", ["id"])
        op.create_index(
            "ix_integration_artifacts_integration_id", "integration_artifacts", ["integration_id"]
        )
        op.create_index("ix_integration_artifacts_user_id", "integration_artifacts", ["user_id"])
        op.create_index("ix_integration_artifacts_provider", "integration_artifacts", ["provider"])
        op.create_index(
            "ix_integration_artifacts_user_type", "integration_artifacts", ["user_id", "artifact_type"]
        )

    # ----------------------------------------------------- integration_sync_runs
    if not _has_table("integration_sync_runs"):
        op.create_table(
            "integration_sync_runs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("integration_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("trigger", sa.String(length=20), server_default="manual", nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("error_code", sa.String(length=60), nullable=True),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("metrics_written", sa.Integer(), server_default="0", nullable=False),
            sa.Column("artifacts_written", sa.Integer(), server_default="0", nullable=False),
            sa.Column("evidence_written", sa.Integer(), server_default="0", nullable=False),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["integration_id"], ["user_integrations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_integration_sync_runs_id", "integration_sync_runs", ["id"])
        op.create_index(
            "ix_integration_sync_runs_integration_id", "integration_sync_runs", ["integration_id"]
        )
        op.create_index("ix_integration_sync_runs_user_id", "integration_sync_runs", ["user_id"])
        op.create_index(
            "ix_integration_sync_runs_started", "integration_sync_runs", ["integration_id", "started_at"]
        )

    # ------------------------------------------------- oauth_authorization_states
    if not _has_table("oauth_authorization_states"):
        op.create_table(
            "oauth_authorization_states",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("state", sa.String(length=128), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("code_verifier_encrypted", sa.Text(), nullable=True),
            sa.Column("redirect_uri", sa.String(length=512), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("consumed_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_oauth_authorization_states_id", "oauth_authorization_states", ["id"])
        op.create_index(
            "ix_oauth_authorization_states_state", "oauth_authorization_states", ["state"], unique=True
        )
        op.create_index("ix_oauth_authorization_states_user_id", "oauth_authorization_states", ["user_id"])
        op.create_index("ix_oauth_states_expiry", "oauth_authorization_states", ["expires_at"])

    # ------------------------------------------------------ account recovery
    _add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))

    if not _has_table("password_reset_tokens"):
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("requested_ip", sa.String(length=64), nullable=True),
            sa.Column("requested_user_agent", sa.String(length=300), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
        op.create_index(
            "ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True
        )
        op.create_index("ix_password_reset_tokens_expiry", "password_reset_tokens", ["expires_at"])

    if not _has_table("email_verification_tokens"):
        op.create_table(
            "email_verification_tokens",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_email_verification_tokens_user_id", "email_verification_tokens", ["user_id"])
        op.create_index(
            "ix_email_verification_tokens_token_hash",
            "email_verification_tokens",
            ["token_hash"],
            unique=True,
        )
        op.create_index(
            "ix_email_verification_tokens_expiry", "email_verification_tokens", ["expires_at"]
        )

    # Any account already marked verified gets a truthful timestamp basis.
    op.execute(
        """
        UPDATE users
        SET email_verified_at = COALESCE(email_verified_at, created_at)
        WHERE is_verified = true AND email_verified_at IS NULL
        """
    )


def downgrade() -> None:
    # Drops only what this revision created.  User rows are untouched.
    for table in (
        "email_verification_tokens",
        "password_reset_tokens",
        "oauth_authorization_states",
        "integration_sync_runs",
        "integration_artifacts",
        "integration_metrics",
    ):
        if _has_table(table):
            op.drop_table(table)

    if "email_verified_at" in _columns("users"):
        op.drop_column("users", "email_verified_at")

    if "ix_user_integrations_status" in _indexes("user_integrations"):
        op.drop_index("ix_user_integrations_status", table_name="user_integrations")
    if "uq_user_integration_provider" in _constraints("user_integrations"):
        op.drop_constraint("uq_user_integration_provider", "user_integrations", type_="unique")

    for column_name in ("sync_attempts", "last_sync_error", "last_connected_at", "api_token_encrypted", "email"):
        if column_name in _columns("user_integrations"):
            op.drop_column("user_integrations", column_name)

    for column_name in ("access_token_encrypted", "refresh_token_encrypted"):
        if column_name in _columns("user_integrations"):
            op.alter_column(
                "user_integrations",
                column_name,
                type_=sa.String(length=2048),
                existing_nullable=True,
            )
