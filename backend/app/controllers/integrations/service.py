"""
Connected Accounts service.

Owns the real connection lifecycle:

    connect  -> persisted CSRF state (+PKCE) -> provider consent -> callback
             -> state validated & consumed -> code exchanged -> identity
                verified -> tokens encrypted & stored -> initial sync

    sync     -> refresh token if expiring -> call provider -> normalize
             -> write metrics/artifacts -> feed evidence pipeline
             -> real timestamps and honest status

    disconnect -> revoke provider-side where supported -> delete credentials
               -> keep historical career evidence -> status NOT_CONNECTED

Nothing here ever returns a token to a caller, and no status is ever set to
CONNECTED/SYNCED without a successful provider response behind it.
"""
from __future__ import annotations

import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.integrations import (
    IntegrationArtifact,
    IntegrationMetric,
    IntegrationSyncRun,
    OAuthAuthorizationState,
    UserIntegration,
)

from . import evidence, normalize
from .crypto import get_cipher
from .providers import (
    AuthMethod,
    BaseConnector,
    ConnectionState,
    EmailConnector,
    LinkOnlyProvider,
    OAuthProvider,
    ProviderError,
    PublicProfileProvider,
    generate_pkce_verifier,
    integration_manager,
    pkce_challenge,
    sanitize_username,
)

#: Refresh a token this long before it actually expires.
TOKEN_REFRESH_MARGIN = timedelta(minutes=5)


class IntegrationServiceError(Exception):
    """User-safe error raised to the router; `detail` stays server-side."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "integration_error",
        status_code: int = 400,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.detail = detail or message


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class IntegrationService:
    def __init__(self) -> None:
        self.manager = integration_manager
        self.cipher = get_cipher()

    # ------------------------------------------------------------- connectors
    def _connector(self, provider_name: str) -> BaseConnector:
        try:
            return self.manager.get(provider_name)
        except ProviderError as exc:
            raise IntegrationServiceError(
                exc.user_message, code=exc.code, status_code=404, detail=exc.detail
            ) from exc

    def redirect_uri(self, provider_name: str) -> str:
        """Absolute callback URI. Built from PUBLIC_BASE_URL, never from HOST."""
        base = settings.PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/api/v1/integrations/{provider_name}/callback"

    # ------------------------------------------------------- OAuth: begin flow
    def begin_oauth(self, db: Session, user_id: int, provider_name: str) -> str:
        """
        Create a single-use, expiring CSRF state (plus a PKCE verifier where the
        provider supports it) and return the provider's authorization URL.
        """
        connector = self._connector(provider_name)
        descriptor = connector.descriptor

        if descriptor.auth_method is not AuthMethod.OAUTH2 or not isinstance(connector, OAuthProvider):
            raise IntegrationServiceError(
                f"{descriptor.display_name} does not use OAuth.",
                code="oauth_not_supported",
                status_code=400,
            )
        if not connector.is_configured():
            missing = ", ".join(connector.missing_configuration())
            raise IntegrationServiceError(
                f"{descriptor.display_name} is not configured on this deployment.",
                code="configuration_required",
                status_code=503,
                detail=f"missing configuration: {missing}",
            )

        self._purge_expired_states(db)

        state = secrets.token_urlsafe(32)
        verifier = generate_pkce_verifier() if connector.supports_pkce else None
        redirect_uri = self.redirect_uri(descriptor.name)

        db.add(
            OAuthAuthorizationState(
                state=state,
                user_id=user_id,
                provider=descriptor.name,
                code_verifier_encrypted=self.cipher.encrypt(verifier),
                redirect_uri=redirect_uri,
                expires_at=_utcnow() + timedelta(seconds=settings.OAUTH_STATE_TTL_SECONDS),
            )
        )

        # Mark the account CONNECTING so the UI can show progress truthfully.
        record = self._get_record(db, user_id, descriptor.name)
        if record is None:
            record = UserIntegration(
                user_id=user_id,
                provider=descriptor.name,
                connection_status=ConnectionState.CONNECTING.value,
                is_active=False,
            )
            db.add(record)
        elif record.connection_status == ConnectionState.NOT_CONNECTED.value:
            record.connection_status = ConnectionState.CONNECTING.value
        db.commit()

        return connector.get_authorization_url(
            state=state,
            redirect_uri=redirect_uri,
            code_challenge=pkce_challenge(verifier) if verifier else None,
        )

    def _purge_expired_states(self, db: Session) -> None:
        db.execute(
            delete(OAuthAuthorizationState).where(OAuthAuthorizationState.expires_at < _utcnow())
        )

    def consume_state(
        self, db: Session, provider_name: str, state: str
    ) -> Tuple[int, Optional[str], str]:
        """
        Validate and single-use-consume an OAuth state.  Returns
        (user_id, code_verifier, redirect_uri).  Raises on anything suspicious.
        """
        if not state:
            raise IntegrationServiceError(
                "This connection request could not be verified. Start again from Connected Accounts.",
                code="invalid_state",
                status_code=400,
                detail="callback arrived with no state parameter",
            )
        record = db.execute(
            select(OAuthAuthorizationState).where(OAuthAuthorizationState.state == state)
        ).scalar_one_or_none()

        if record is None or record.provider != provider_name.lower():
            raise IntegrationServiceError(
                "This connection request could not be verified. Start again from Connected Accounts.",
                code="invalid_state",
                status_code=400,
                detail=f"state not found or provider mismatch (provider={provider_name})",
            )
        if record.consumed_at is not None:
            raise IntegrationServiceError(
                "This connection link was already used. Start again from Connected Accounts.",
                code="state_replayed",
                status_code=400,
                detail=f"state replay attempt for provider={provider_name} user={record.user_id}",
            )
        if record.expires_at < _utcnow():
            raise IntegrationServiceError(
                "This connection request expired. Start again from Connected Accounts.",
                code="state_expired",
                status_code=400,
                detail=f"state expired for provider={provider_name}",
            )

        record.consumed_at = _utcnow()
        verifier = self.cipher.decrypt(record.code_verifier_encrypted)
        redirect_uri = record.redirect_uri
        user_id = record.user_id
        db.commit()
        return user_id, verifier, redirect_uri

    # ---------------------------------------------------- OAuth: finish flow
    async def complete_oauth(
        self,
        db: Session,
        user_id: int,
        provider_name: str,
        code: str,
        code_verifier: Optional[str],
        redirect_uri: str,
    ) -> UserIntegration:
        connector = self._connector(provider_name)
        if not isinstance(connector, OAuthProvider):
            raise IntegrationServiceError(
                "That platform does not use OAuth.", code="oauth_not_supported"
            )

        try:
            tokens = await connector.exchange_code(code, redirect_uri, code_verifier)
            profile = await connector.get_user_profile(tokens["access_token"])
        except ProviderError as exc:
            logger.warning("OAuth completion failed for %s: %s", provider_name, exc.detail)
            self._mark_failure(db, user_id, provider_name, exc)
            raise IntegrationServiceError(
                exc.user_message, code=exc.code, detail=exc.detail
            ) from exc

        if not profile.get("provider_account_id"):
            raise IntegrationServiceError(
                f"{connector.descriptor.display_name} did not return an account identity, "
                "so the connection was not saved.",
                code="identity_verification_failed",
                detail=f"{provider_name} profile had no provider_account_id",
            )

        record = self._upsert(
            db,
            user_id=user_id,
            connector=connector,
            profile=profile,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens.get("expires_in"),
            scope=tokens.get("scope") or " ".join(connector.descriptor.scopes),
        )

        # Initial sync right after connecting (spec §17).
        await self.sync(db, user_id, provider_name, trigger="initial")
        db.refresh(record)
        return record

    # ------------------------------------------- public profile / link only
    async def link_account(
        self,
        db: Session,
        user_id: int,
        provider_name: str,
        identifier: str,
        api_token: Optional[str] = None,
    ) -> UserIntegration:
        """
        Connect a platform that has no OAuth: a public username, or a link-only
        platform.  No third-party password is ever accepted here — `api_token`
        is only used by connectors that declare `supports_api_token`.
        """
        connector = self._connector(provider_name)
        descriptor = connector.descriptor

        if descriptor.auth_method is AuthMethod.OAUTH2:
            raise IntegrationServiceError(
                f"{descriptor.display_name} must be connected with OAuth.",
                code="oauth_required",
            )
        if api_token and not getattr(connector, "supports_api_token", False):
            raise IntegrationServiceError(
                f"{descriptor.display_name} does not accept an API token.",
                code="token_not_supported",
            )

        try:
            username = sanitize_username(identifier)
            profile = await connector.validate_and_get_profile(username)  # type: ignore[attr-defined]
        except ProviderError as exc:
            logger.info("Linking %s failed: %s", provider_name, exc.detail)
            raise IntegrationServiceError(
                exc.user_message, code=exc.code, detail=exc.detail
            ) from exc

        record = self._upsert(
            db,
            user_id=user_id,
            connector=connector,
            profile=profile,
            api_token=api_token,
        )

        if descriptor.auth_method is AuthMethod.LINK_ONLY:
            # Nothing to sync, and we say so instead of faking a sync.
            record.connection_status = ConnectionState.LIMITED.value
            record.last_sync_status = None
            record.last_synced_at = None
            record.telemetry_data = {"limitation_note": descriptor.limitation_note}
            db.commit()
            db.refresh(record)
            return record

        await self.sync(db, user_id, provider_name, trigger="initial")
        db.refresh(record)
        return record

    # ------------------------------------------------------------------ upsert
    def _upsert(
        self,
        db: Session,
        *,
        user_id: int,
        connector: BaseConnector,
        profile: Dict[str, Any],
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        api_token: Optional[str] = None,
        expires_in: Optional[Any] = None,
        scope: Optional[str] = None,
    ) -> UserIntegration:
        provider_name = connector.descriptor.name
        record = self._get_record(db, user_id, provider_name)
        if record is None:
            record = UserIntegration(user_id=user_id, provider=provider_name)
            db.add(record)

        account_id = profile.get("provider_account_id")
        record.provider_account_id = str(account_id) if account_id is not None else None
        record.provider_username = profile.get("provider_username")
        record.display_name = profile.get("display_name")
        record.email = profile.get("email")
        record.profile_url = profile.get("profile_url")
        record.avatar_url = profile.get("avatar_url")
        record.is_active = True
        record.last_connected_at = _utcnow()
        record.sync_attempts = 0
        record.last_sync_error = None
        record.last_error = None

        if access_token:
            record.access_token_encrypted = self.cipher.encrypt(access_token)
        if refresh_token:
            record.refresh_token_encrypted = self.cipher.encrypt(refresh_token)
        if api_token:
            record.api_token_encrypted = self.cipher.encrypt(api_token)
        if scope:
            record.scopes = scope[:1024]

        record.token_expires_at = self._expiry(expires_in)

        # Authenticated, but data breadth may still be limited.
        record.connection_status = (
            ConnectionState.LIMITED.value
            if getattr(connector, "always_limited", False)
            else ConnectionState.CONNECTED.value
        )

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def _expiry(expires_in: Optional[Any]) -> Optional[datetime]:
        try:
            seconds = int(expires_in) if expires_in is not None else None
        except (TypeError, ValueError):
            return None
        if not seconds or seconds <= 0:
            return None
        return _utcnow() + timedelta(seconds=seconds)

    def _get_record(self, db: Session, user_id: int, provider_name: str) -> Optional[UserIntegration]:
        return db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.provider == provider_name.lower(),
            )
        ).scalar_one_or_none()

    # -------------------------------------------------------------------- sync
    async def sync(
        self,
        db: Session,
        user_id: int,
        provider_name: str,
        *,
        trigger: str = "manual",
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Run a real synchronization.  Returns a sanitized summary; raises
        IntegrationServiceError only for conditions the caller must handle
        (not connected, not syncable).  Provider failures are recorded on the
        record and reported in the return value.
        """
        connector = self._connector(provider_name)
        descriptor = connector.descriptor
        record = self._get_record(db, user_id, descriptor.name)

        if record is None or not record.is_active:
            raise IntegrationServiceError(
                f"{descriptor.display_name} is not connected.",
                code="not_connected",
                status_code=404,
            )
        if descriptor.auth_method is AuthMethod.LINK_ONLY or isinstance(connector, LinkOnlyProvider):
            raise IntegrationServiceError(
                descriptor.limitation_note or f"{descriptor.display_name} cannot be synchronized.",
                code="sync_not_supported",
                status_code=409,
            )

        # Throttle: protect the provider and ourselves (spec §17).
        if not force and record.last_synced_at and trigger == "manual":
            elapsed = (_utcnow() - record.last_synced_at).total_seconds()
            if elapsed < settings.SYNC_MIN_INTERVAL_SECONDS:
                wait = int(settings.SYNC_MIN_INTERVAL_SECONDS - elapsed)
                raise IntegrationServiceError(
                    f"{descriptor.display_name} was just synced. Try again in {wait}s.",
                    code="sync_throttled",
                    status_code=429,
                )

        run = IntegrationSyncRun(
            integration_id=record.id,
            user_id=user_id,
            provider=descriptor.name,
            trigger=trigger,
            status="RUNNING",
            started_at=_utcnow(),
        )
        db.add(run)
        record.connection_status = ConnectionState.SYNCING.value
        db.commit()

        started = _utcnow()
        try:
            telemetry = await self._fetch_telemetry(db, record, connector)
        except ProviderError as exc:
            return self._finish_failed_run(db, record, run, exc, started)

        normalized = normalize.normalize(descriptor.name, telemetry)
        metrics_written = self._write_metrics(db, record, normalized)
        artifacts_written = self._write_artifacts(db, record, normalized)
        skills_written, pipeline = evidence.apply_all(db, user_id, normalized)

        record.telemetry_data = normalized.summary
        record.last_synced_at = _utcnow()
        record.last_sync_status = "SUCCESS"
        record.last_sync_error = None
        record.last_error = None
        record.sync_attempts = 0
        record.connection_status = (
            ConnectionState.LIMITED.value
            if getattr(connector, "always_limited", False)
            or (descriptor.limitation_note and not normalized.metrics)
            else ConnectionState.SYNCED.value
        )

        run.status = "SYNCED"
        run.finished_at = _utcnow()
        run.duration_ms = int((run.finished_at - started).total_seconds() * 1000)
        run.metrics_written = metrics_written
        run.artifacts_written = artifacts_written
        run.evidence_written = skills_written + sum(pipeline.values())
        db.commit()
        db.refresh(record)

        return {
            "provider": descriptor.name,
            "status": record.connection_status,
            "last_synced_at": record.last_synced_at.isoformat(),
            "metrics_written": metrics_written,
            "artifacts_written": artifacts_written,
            "skills_written": skills_written,
            "pipeline": pipeline,
            "summary": self.public_summary(record, connector),
        }

    async def _fetch_telemetry(
        self, db: Session, record: UserIntegration, connector: BaseConnector
    ) -> Dict[str, Any]:
        """
        Call the provider, refreshing the access token first when it is close to
        expiry.  Retries only retryable failures, with bounded exponential
        backoff — never an infinite loop (spec §17).
        """
        attempts = max(1, settings.SYNC_MAX_ATTEMPTS)
        last_error: Optional[ProviderError] = None

        for attempt in range(attempts):
            try:
                if isinstance(connector, OAuthProvider):
                    access_token = await self._usable_access_token(db, record, connector)
                    identifier = record.provider_username or record.provider_account_id or ""
                    return await connector.get_telemetry(access_token, identifier)

                if isinstance(connector, PublicProfileProvider):
                    identifier = record.provider_username or record.provider_account_id or ""
                    if getattr(connector, "supports_api_token", False):
                        api_token = self.cipher.decrypt(record.api_token_encrypted)
                        return await connector.get_telemetry(identifier, api_token=api_token)  # type: ignore[call-arg]
                    return await connector.get_telemetry(identifier)

                raise ProviderError(
                    f"{connector.descriptor.display_name} cannot be synchronized.",
                    code="sync_not_supported",
                )
            except ProviderError as exc:
                last_error = exc
                if not exc.retryable or attempt == attempts - 1:
                    raise
                delay = settings.SYNC_BACKOFF_BASE_SECONDS ** (attempt + 1)
                retry_after = getattr(exc, "retry_after", None)
                if retry_after:
                    delay = min(float(retry_after), 30.0)
                logger.info(
                    "Retrying %s sync in %.1fs after %s", connector.provider_name, delay, exc.code
                )
                await asyncio.sleep(delay)

        raise last_error or ProviderError("Synchronization failed.", code="provider_error")

    async def _usable_access_token(
        self, db: Session, record: UserIntegration, connector: OAuthProvider
    ) -> str:
        access_token = self.cipher.decrypt(record.access_token_encrypted)
        expires_at = record.token_expires_at
        needs_refresh = bool(
            expires_at and expires_at - TOKEN_REFRESH_MARGIN <= _utcnow()
        ) or not access_token

        if needs_refresh:
            refresh = self.cipher.decrypt(record.refresh_token_encrypted)
            if not refresh:
                raise ProviderError(
                    f"{connector.descriptor.display_name} authorization expired. Reconnect required.",
                    code="reauth_required",
                    requires_reauth=True,
                    detail=f"{record.provider}: no usable refresh token",
                )
            refreshed = await connector.refresh_token(refresh)
            access_token = refreshed["access_token"]
            record.access_token_encrypted = self.cipher.encrypt(access_token)
            if refreshed.get("refresh_token"):
                record.refresh_token_encrypted = self.cipher.encrypt(refreshed["refresh_token"])
            record.token_expires_at = self._expiry(refreshed.get("expires_in"))
            db.commit()

        if not access_token:
            raise ProviderError(
                f"{connector.descriptor.display_name} authorization is unavailable. Reconnect required.",
                code="reauth_required",
                requires_reauth=True,
                detail=f"{record.provider}: access token could not be decrypted",
            )
        return access_token

    def _finish_failed_run(
        self,
        db: Session,
        record: UserIntegration,
        run: IntegrationSyncRun,
        exc: ProviderError,
        started: datetime,
    ) -> Dict[str, Any]:
        # Technical detail to the log, user-safe message to the record.
        logger.warning("Sync failed for %s: %s", record.provider, exc.detail)

        record.sync_attempts = (record.sync_attempts or 0) + 1
        record.last_sync_status = "FAILED"
        record.last_sync_error = exc.user_message[:500]
        record.last_error = exc.user_message[:1024]
        record.connection_status = (
            ConnectionState.REAUTH_REQUIRED.value
            if exc.requires_reauth
            else ConnectionState.SYNC_FAILED.value
        )
        if exc.requires_reauth:
            # The stored credential is useless; do not keep it around.
            record.access_token_encrypted = None
            record.token_expires_at = None

        run.status = record.connection_status
        run.error_code = exc.code
        run.error_message = exc.user_message[:500]
        run.finished_at = _utcnow()
        run.duration_ms = int((run.finished_at - started).total_seconds() * 1000)
        db.commit()
        db.refresh(record)

        return {
            "provider": record.provider,
            "status": record.connection_status,
            "last_synced_at": record.last_synced_at.isoformat() if record.last_synced_at else None,
            "error": {"code": exc.code, "message": exc.user_message},
            "retryable": exc.retryable,
            "requires_reauth": exc.requires_reauth,
        }

    # -------------------------------------------------------- normalized rows
    def _write_metrics(
        self, db: Session, record: UserIntegration, normalized: normalize.NormalizedTelemetry
    ) -> int:
        written = 0
        for metric in normalized.metrics:
            existing = db.execute(
                select(IntegrationMetric).where(
                    IntegrationMetric.integration_id == record.id,
                    IntegrationMetric.metric_key == metric.key,
                )
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    IntegrationMetric(
                        integration_id=record.id,
                        user_id=record.user_id,
                        provider=record.provider,
                        metric_key=metric.key,
                        metric_value=metric.value,
                        metric_text=metric.text,
                        unit=metric.unit,
                        captured_at=_utcnow(),
                    )
                )
            else:
                existing.metric_value = metric.value
                existing.metric_text = metric.text
                existing.unit = metric.unit
                existing.captured_at = _utcnow()
            written += 1
        return written

    def _write_artifacts(
        self, db: Session, record: UserIntegration, normalized: normalize.NormalizedTelemetry
    ) -> int:
        written = 0
        for artifact in normalized.artifacts:
            existing = db.execute(
                select(IntegrationArtifact).where(
                    IntegrationArtifact.integration_id == record.id,
                    IntegrationArtifact.artifact_type == artifact.artifact_type,
                    IntegrationArtifact.external_id == artifact.external_id,
                )
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    IntegrationArtifact(
                        integration_id=record.id,
                        user_id=record.user_id,
                        provider=record.provider,
                        artifact_type=artifact.artifact_type,
                        external_id=artifact.external_id[:500],
                        title=artifact.title,
                        description=artifact.description,
                        url=artifact.url,
                        primary_language=artifact.primary_language,
                        stars=artifact.stars,
                        forks=artifact.forks,
                        downloads=artifact.downloads,
                        likes=artifact.likes,
                        occurred_at=artifact.occurred_at,
                        attributes=artifact.attributes,
                        first_seen_at=_utcnow(),
                        last_seen_at=_utcnow(),
                    )
                )
            else:
                existing.title = artifact.title or existing.title
                existing.description = artifact.description or existing.description
                existing.url = artifact.url or existing.url
                existing.primary_language = artifact.primary_language or existing.primary_language
                existing.stars = artifact.stars
                existing.forks = artifact.forks
                existing.downloads = artifact.downloads
                existing.likes = artifact.likes
                existing.occurred_at = artifact.occurred_at or existing.occurred_at
                existing.attributes = artifact.attributes or existing.attributes
                existing.last_seen_at = _utcnow()
            written += 1
        return written

    def _mark_failure(
        self, db: Session, user_id: int, provider_name: str, exc: ProviderError
    ) -> None:
        record = self._get_record(db, user_id, provider_name)
        if record is None:
            return
        record.connection_status = (
            ConnectionState.REAUTH_REQUIRED.value
            if exc.requires_reauth
            else ConnectionState.NOT_CONNECTED.value
            if not record.is_active
            else ConnectionState.SYNC_FAILED.value
        )
        record.last_sync_error = exc.user_message[:500]
        db.commit()

    # -------------------------------------------------------------- disconnect
    async def disconnect(
        self, db: Session, user_id: int, provider_name: str, *, purge_evidence: bool = False
    ) -> Dict[str, Any]:
        """
        Real disconnect: revoke provider-side where the provider offers it,
        delete every stored credential, and reset the record to NOT_CONNECTED.

        Imported career evidence (repositories, solved problems, applications)
        is RETAINED by default — it is the user's career history — unless
        `purge_evidence` is requested.
        """
        connector = self._connector(provider_name)
        record = self._get_record(db, user_id, connector.descriptor.name)
        if record is None or not record.is_active:
            raise IntegrationServiceError(
                f"{connector.descriptor.display_name} is not connected.",
                code="not_connected",
                status_code=404,
            )

        revoked = False
        if isinstance(connector, OAuthProvider):
            access_token = self.cipher.decrypt(record.access_token_encrypted)
            refresh_token = self.cipher.decrypt(record.refresh_token_encrypted)
            if access_token or refresh_token:
                try:
                    revoked = await connector.revoke_token(access_token or "", refresh_token)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Token revocation failed for %s: %r", provider_name, exc)
                    revoked = False

        # Credentials go regardless of whether revocation succeeded.
        record.access_token_encrypted = None
        record.refresh_token_encrypted = None
        record.api_token_encrypted = None
        record.token_expires_at = None
        record.scopes = None
        record.is_active = False
        record.connection_status = ConnectionState.NOT_CONNECTED.value
        record.telemetry_data = {}
        record.last_sync_status = None
        record.last_sync_error = None
        record.last_error = None
        record.sync_attempts = 0

        removed = {"metrics": 0, "artifacts": 0}
        # Live platform metrics describe a connection that no longer exists.
        metric_count = db.execute(
            select(IntegrationMetric).where(IntegrationMetric.integration_id == record.id)
        ).scalars().all()
        removed["metrics"] = len(metric_count)
        db.execute(delete(IntegrationMetric).where(IntegrationMetric.integration_id == record.id))

        if purge_evidence:
            artifacts = db.execute(
                select(IntegrationArtifact).where(IntegrationArtifact.integration_id == record.id)
            ).scalars().all()
            removed["artifacts"] = len(artifacts)
            db.execute(
                delete(IntegrationArtifact).where(IntegrationArtifact.integration_id == record.id)
            )

        db.commit()
        return {
            "provider": connector.descriptor.name,
            "status": ConnectionState.NOT_CONNECTED.value,
            "token_revoked_at_provider": revoked,
            "removed": removed,
            "evidence_retained": not purge_evidence,
        }

    # ------------------------------------------------------------------ reads
    def public_summary(
        self, record: Optional[UserIntegration], connector: BaseConnector
    ) -> Dict[str, Any]:
        """Sanitized telemetry summary. Contains no token and no raw provider body."""
        if record is None or not record.telemetry_data:
            return {}
        summary = dict(record.telemetry_data)
        for forbidden in ("job_events", "access_token", "refresh_token", "api_token"):
            summary.pop(forbidden, None)
        if connector.descriptor.limitation_note and "limitation_note" not in summary:
            summary["limitation_note"] = connector.descriptor.limitation_note
        return summary

    def account_view(
        self, db: Session, record: Optional[UserIntegration], connector: BaseConnector
    ) -> Dict[str, Any]:
        descriptor = connector.descriptor
        connected = bool(record and record.is_active and record.provider_account_id)
        status = (
            record.connection_status
            if record and record.is_active
            else self.manager.default_state(descriptor.name).value
        )

        external_url = None
        if connected and record is not None:
            external_url = connector.get_external_url(
                {"profile_url": record.profile_url, "provider_username": record.provider_username}
            )

        artifact_counts: Dict[str, int] = {}
        if record is not None:
            rows = db.execute(
                select(IntegrationArtifact.artifact_type, IntegrationArtifact.id).where(
                    IntegrationArtifact.integration_id == record.id
                )
            ).all()
            for artifact_type, _ in rows:
                artifact_counts[artifact_type] = artifact_counts.get(artifact_type, 0) + 1

        return {
            "provider": descriptor.name,
            "display_name": descriptor.display_name,
            "auth_method": descriptor.auth_method.value,
            "connected": connected,
            "status": status,
            "capabilities": sorted(c.value for c in descriptor.capabilities),
            "supports_sync": descriptor.auth_method is not AuthMethod.LINK_ONLY,
            "supports_api_token": bool(getattr(connector, "supports_api_token", False)),
            "api_token_label": getattr(connector, "api_token_label", None),
            "api_token_help": getattr(connector, "api_token_help", None),
            "configured": connector.is_configured(),
            "missing_configuration": connector.missing_configuration(),
            "limitation_note": descriptor.limitation_note,
            "docs_url": descriptor.docs_url,
            "username": record.provider_username if connected else None,
            "display_label": record.display_name if connected else None,
            "email": record.email if connected else None,
            "avatar_url": record.avatar_url if connected else None,
            "external_url": external_url,
            "scopes": (record.scopes.split() if connected and record.scopes else list(descriptor.scopes)),
            "last_connected_at": (
                record.last_connected_at.isoformat() if record and record.last_connected_at else None
            ),
            "last_synced_at": (
                record.last_synced_at.isoformat() if record and record.last_synced_at else None
            ),
            "last_sync_status": record.last_sync_status if record else None,
            "last_sync_error": record.last_sync_error if record else None,
            "summary": self.public_summary(record, connector) if connected else {},
            "artifact_counts": artifact_counts,
        }

    def list_accounts(self, db: Session, user_id: int) -> Dict[str, Any]:
        records = {
            r.provider: r
            for r in db.execute(
                select(UserIntegration).where(UserIntegration.user_id == user_id)
            ).scalars().all()
        }
        accounts = [
            self.account_view(db, records.get(connector.descriptor.name), connector)
            for connector in self.manager.all()
        ]
        return {
            "total_providers": len(accounts),
            "total_connected": sum(1 for a in accounts if a["connected"]),
            "accounts": accounts,
            # Keyed form kept for the existing frontend contract.
            "platforms": {a["provider"]: a for a in accounts},
        }

    def get_account(self, db: Session, user_id: int, provider_name: str) -> Dict[str, Any]:
        connector = self._connector(provider_name)
        record = self._get_record(db, user_id, connector.descriptor.name)
        return self.account_view(db, record, connector)

    async def health(self, db: Session, user_id: int, provider_name: str) -> Dict[str, Any]:
        connector = self._connector(provider_name)
        record = self._get_record(db, user_id, connector.descriptor.name)
        probe = await connector.health_check()
        return {
            **probe,
            "connection_status": (
                record.connection_status
                if record and record.is_active
                else self.manager.default_state(connector.descriptor.name).value
            ),
            "last_synced_at": (
                record.last_synced_at.isoformat() if record and record.last_synced_at else None
            ),
            "token_expires_at": (
                record.token_expires_at.isoformat() if record and record.token_expires_at else None
            ),
            "checked_at": _utcnow().isoformat(),
        }

    async def sync_all(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Sync every syncable connected account, reporting each result honestly."""
        records = db.execute(
            select(UserIntegration).where(
                UserIntegration.user_id == user_id,
                UserIntegration.is_active.is_(True),
            )
        ).scalars().all()

        results: List[Dict[str, Any]] = []
        for record in records:
            if not self.manager.has(record.provider):
                continue
            connector = self.manager.get(record.provider)
            if connector.descriptor.auth_method is AuthMethod.LINK_ONLY:
                results.append(
                    {
                        "provider": record.provider,
                        "status": ConnectionState.LIMITED.value,
                        "skipped": True,
                        "reason": connector.descriptor.limitation_note,
                    }
                )
                continue
            try:
                results.append(await self.sync(db, user_id, record.provider, trigger="scheduled"))
            except IntegrationServiceError as exc:
                results.append(
                    {
                        "provider": record.provider,
                        "status": record.connection_status,
                        "skipped": True,
                        "reason": exc.message,
                    }
                )
        return results

    def catalog(self) -> List[Dict[str, Any]]:
        return self.manager.catalog()


#: Shared instance used by the router.
integration_service = IntegrationService()
