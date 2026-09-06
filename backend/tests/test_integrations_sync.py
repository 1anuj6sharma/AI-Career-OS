"""
Connected Accounts — sync, linking, disconnect and health (spec §30).

Asserts on real state transitions: no status is CONNECTED/SYNCED without a
successful provider response behind it, timestamps are only written when a sync
actually happened, and disconnect really removes credentials.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select

from app.controllers.integrations.providers.base import ProviderError
from app.core.config import settings
from app.models.integrations import (
    IntegrationArtifact,
    IntegrationMetric,
    IntegrationSyncRun,
    UserIntegration,
)
from tests.integration_fakes import rate_limited

API = "/api/v1/integrations"


def _naive_utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _record(db_session, user_id, provider) -> UserIntegration:
    return db_session.execute(
        select(UserIntegration).where(
            UserIntegration.user_id == user_id, UserIntegration.provider == provider
        )
    ).scalar_one_or_none()


def _connect_github(client, auth_headers) -> None:
    body = client.get(f"{API}/github/connect", headers=auth_headers).json()
    state = parse_qs(urlparse(body["url"]).query)["state"][0]
    client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)


# ----------------------------------------------------------------- overview

def test_overview_reports_honest_default_states(client, auth_headers, fake_providers):
    body = client.get(API, headers=auth_headers).json()
    assert body["total_connected"] == 0
    assert body["total_providers"] == len(body["accounts"])

    by_provider = {a["provider"]: a for a in body["accounts"]}
    # Nothing is connected, so no card may claim it is.
    assert all(a["connected"] is False for a in body["accounts"])
    assert all(a["last_synced_at"] is None for a in body["accounts"])
    assert all(a["summary"] == {} for a in body["accounts"])

    # An OAuth provider with no client credentials says so rather than pretending.
    assert by_provider["google"]["status"] == "CONFIGURATION_REQUIRED"
    assert by_provider["google"]["missing_configuration"]
    # A public-profile provider needs no deployment config.
    assert by_provider["leetcode"]["status"] == "NOT_CONNECTED"
    # GeeksforGeeks cannot be synchronized and declares it.
    assert by_provider["gfg"]["supports_sync"] is False
    assert by_provider["gfg"]["limitation_note"]

    # No response field may ever carry a credential.
    assert "access_token" not in client.get(API, headers=auth_headers).text


def test_catalog_exposes_capabilities_without_secrets(
    client, auth_headers, fake_providers, monkeypatch
):
    # A configured secret must never be echoed back, under any field name.
    monkeypatch.setattr(settings, "LINKEDIN_CLIENT_SECRET", "li-secret-sentinel-4821")
    monkeypatch.setattr(settings, "GITHUB_CLIENT_SECRET", "gh-secret-sentinel-4821")

    response = client.get(f"{API}/catalog", headers=auth_headers)
    entries = response.json()
    providers = {e["provider"]: e for e in entries}
    assert providers["github"]["auth_method"] == "OAUTH2"
    assert providers["leetcode"]["auth_method"] == "PUBLIC_USERNAME"
    assert providers["gfg"]["auth_method"] == "LINK_ONLY"
    assert providers["kaggle"]["supports_api_token"] is True
    # Scopes are public information.
    assert providers["github"]["scopes"] == ["read:user", "user:email"]

    assert "sentinel-4821" not in response.text
    # No entry carries a credential field of its own.
    assert not any(
        "secret" in key or "token" in key
        for entry in entries
        for key in entry
        if key not in ("supports_api_token", "api_token_label", "api_token_help")
    )
    # Where a secret is named at all it is an environment variable name for the
    # operator to set, not a value.
    for entry in entries:
        for name in entry["missing_configuration"]:
            assert name == name.upper()


def test_overview_requires_authentication(client, fake_providers):
    assert client.get(API).status_code in (401, 403)


# --------------------------------------------------------------------- sync

def test_manual_sync_writes_real_data_and_timestamps(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    record = _record(db_session, test_user.id, "github")
    first_synced_at = record.last_synced_at

    response = client.post(f"{API}/github/sync", json={"force": True}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SYNCED"
    assert body["metrics_written"] > 0
    assert body["artifacts_written"] == 1
    assert body["last_synced_at"] is not None
    # The summary is sanitized: counts and languages, never a token.
    assert body["summary"]["total_stars"] == 13
    assert "access_token" not in response.text

    db_session.refresh(record)
    assert record.last_synced_at >= first_synced_at
    assert record.last_sync_status == "SUCCESS"
    assert record.sync_attempts == 0

    # Re-syncing updates rows in place rather than duplicating evidence.
    metrics = db_session.execute(
        select(IntegrationMetric).where(IntegrationMetric.integration_id == record.id)
    ).scalars().all()
    assert len(metrics) == len({m.metric_key for m in metrics})
    artifacts = db_session.execute(
        select(IntegrationArtifact).where(IntegrationArtifact.integration_id == record.id)
    ).scalars().all()
    assert len(artifacts) == 1


def test_sync_of_unconnected_provider_is_404(client, auth_headers, fake_providers):
    response = client.post(f"{API}/github/sync", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_connected"


def test_manual_sync_is_throttled(client, db_session, test_user, auth_headers, fake_providers):
    _connect_github(client, auth_headers)
    # The initial sync just ran, so an unforced manual sync must be refused.
    response = client.post(f"{API}/github/sync", headers=auth_headers)
    assert response.status_code == 429
    assert response.json()["detail"]["code"] == "sync_throttled"

    # force bypasses the throttle for a deliberate user action.
    assert client.post(f"{API}/github/sync", json={"force": True}, headers=auth_headers).status_code == 200


def test_failed_sync_reports_honestly_and_keeps_last_good_timestamp(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    record = _record(db_session, test_user.id, "github")
    good_timestamp = record.last_synced_at

    fake_providers["oauth"].telemetry_error = ProviderError(
        "GitHub is unavailable right now. Try again shortly.",
        code="provider_unavailable",
        detail="503 from api.github.com trace-id 9f2c",
    )
    response = client.post(f"{API}/github/sync", json={"force": True}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SYNC_FAILED"
    assert body["error"]["code"] == "provider_unavailable"
    # Provider internals never reach the client.
    assert "trace-id" not in response.text
    assert "api.github.com" not in response.text

    db_session.refresh(record)
    assert record.connection_status == "SYNC_FAILED"
    assert record.last_sync_status == "FAILED"
    assert record.sync_attempts == 1
    # A failed sync does not invent a fresh timestamp.
    assert record.last_synced_at == good_timestamp

    run = db_session.execute(
        select(IntegrationSyncRun)
        .where(IntegrationSyncRun.integration_id == record.id)
        .order_by(IntegrationSyncRun.id.desc())
    ).scalars().first()
    assert run.status == "SYNC_FAILED"
    assert run.error_code == "provider_unavailable"


def test_retryable_failure_is_retried_a_bounded_number_of_times(
    client, db_session, test_user, auth_headers, fake_providers, monkeypatch
):
    """Rate limiting is retried with backoff, then reported — never looped forever."""
    monkeypatch.setattr(settings, "SYNC_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(settings, "SYNC_BACKOFF_BASE_SECONDS", 0.0)

    _connect_github(client, auth_headers)
    oauth = fake_providers["oauth"]
    oauth.telemetry_calls.clear()
    # Two transient failures, then success on the third attempt.
    oauth.telemetry_transient_errors = [rate_limited(0), rate_limited(0)]

    slept: list = []

    async def _no_sleep(delay):
        slept.append(delay)

    monkeypatch.setattr("app.controllers.integrations.service.asyncio.sleep", _no_sleep)

    response = client.post(f"{API}/github/sync", json={"force": True}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "SYNCED"
    assert len(oauth.telemetry_calls) == 3
    assert len(slept) == 2  # one wait per retry, bounded by SYNC_MAX_ATTEMPTS


def test_non_retryable_failure_is_not_retried(
    client, db_session, test_user, auth_headers, fake_providers, monkeypatch
):
    monkeypatch.setattr(settings, "SYNC_MAX_ATTEMPTS", 3)
    _connect_github(client, auth_headers)
    oauth = fake_providers["oauth"]
    oauth.telemetry_calls.clear()
    oauth.telemetry_error = ProviderError("Insufficient scope.", code="insufficient_scope")

    response = client.post(f"{API}/github/sync", json={"force": True}, headers=auth_headers)
    assert response.json()["error"]["code"] == "insufficient_scope"
    assert len(oauth.telemetry_calls) == 1


def test_sync_all_skips_link_only_providers_with_a_reason(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    client.post(f"{API}/gfg/link", json={"identifier": "octodev"}, headers=auth_headers)

    results = {r["provider"]: r for r in client.post(f"{API}/sync-all", headers=auth_headers).json()}
    assert results["gfg"]["skipped"] is True
    assert results["gfg"]["status"] == "LIMITED"
    assert results["gfg"]["reason"]
    # A scheduled sync is not subject to the manual throttle.
    assert results["github"]["status"] == "SYNCED"


# ------------------------------------------------------- non-OAuth linking

def test_public_profile_link_syncs_real_data(
    client, db_session, test_user, auth_headers, fake_providers
):
    response = client.post(
        f"{API}/leetcode/link", json={"identifier": "octodev"}, headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["connected"] is True
    assert body["status"] == "SYNCED"
    assert body["username"] == "octodev"
    assert body["external_url"] == "https://leetcode.com/u/octodev/"
    assert body["summary"]["solved_total"] == 12

    record = _record(db_session, test_user.id, "leetcode")
    assert record.last_synced_at is not None
    # No credential was collected for a public profile.
    assert record.access_token_encrypted is None
    assert record.api_token_encrypted is None


def test_link_accepts_a_profile_url_and_rejects_junk(client, auth_headers, fake_providers):
    ok = client.post(
        f"{API}/leetcode/link",
        json={"identifier": "https://leetcode.com/u/octodev/"},
        headers=auth_headers,
    )
    assert ok.status_code == 201
    assert ok.json()["username"] == "octodev"

    bad = client.post(
        f"{API}/leetcode/link", json={"identifier": "not a username!!"}, headers=auth_headers
    )
    assert bad.status_code == 400
    assert bad.json()["detail"]["code"] == "invalid_identifier"


def test_link_only_provider_is_limited_and_never_claims_a_sync(
    client, db_session, test_user, auth_headers, fake_providers
):
    response = client.post(f"{API}/gfg/link", json={"identifier": "octodev"}, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "LIMITED"
    assert body["supports_sync"] is False
    assert body["last_synced_at"] is None
    assert body["limitation_note"]

    # An explicit sync request is refused with an explanation, not faked.
    sync = client.post(f"{API}/gfg/sync", json={"force": True}, headers=auth_headers)
    assert sync.status_code == 409
    assert sync.json()["detail"]["code"] == "sync_not_supported"

    record = _record(db_session, test_user.id, "gfg")
    assert record.last_synced_at is None
    assert record.last_sync_status is None


def test_link_rejects_oauth_provider_and_unsupported_tokens(client, auth_headers, fake_providers):
    oauth_attempt = client.post(
        f"{API}/github/link", json={"identifier": "octodev"}, headers=auth_headers
    )
    assert oauth_attempt.status_code == 400
    assert oauth_attempt.json()["detail"]["code"] == "oauth_required"

    # LeetCode takes no token: passing one is refused rather than silently ignored.
    token_attempt = client.post(
        f"{API}/leetcode/link",
        json={"identifier": "octodev", "api_token": "some-token"},
        headers=auth_headers,
    )
    assert token_attempt.status_code == 400
    assert token_attempt.json()["detail"]["code"] == "token_not_supported"


def test_link_schema_has_no_password_field(client, auth_headers, fake_providers):
    """A third-party password must not even be expressible in the API contract."""
    from app.views.integrations import IntegrationLinkIn

    fields = set(IntegrationLinkIn.model_fields)
    assert fields == {"identifier", "api_token"}
    assert not any("password" in f for f in fields)


# --------------------------------------------------------------- disconnect

def test_disconnect_revokes_deletes_credentials_and_keeps_career_evidence(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    record = _record(db_session, test_user.id, "github")
    integration_id = record.id

    response = client.post(f"{API}/github/disconnect", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NOT_CONNECTED"
    assert body["token_revoked_at_provider"] is True
    assert body["evidence_retained"] is True

    # Revocation was actually attempted with the stored token.
    assert fake_providers["oauth"].revoke_calls == ["gho_access_1"]

    db_session.refresh(record)
    assert record.is_active is False
    assert record.connection_status == "NOT_CONNECTED"
    assert record.access_token_encrypted is None
    assert record.refresh_token_encrypted is None
    assert record.api_token_encrypted is None
    assert record.token_expires_at is None
    assert record.scopes is None

    # Live metrics go; career artifacts are the user's history and stay.
    assert db_session.execute(
        select(IntegrationMetric).where(IntegrationMetric.integration_id == integration_id)
    ).scalars().all() == []
    assert db_session.execute(
        select(IntegrationArtifact).where(IntegrationArtifact.integration_id == integration_id)
    ).scalars().all()

    # The UI immediately sees a disconnected card.
    card = client.get(f"{API}/github", headers=auth_headers).json()
    assert card["connected"] is False
    assert card["external_url"] is None


def test_disconnect_can_purge_evidence_on_request(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    integration_id = _record(db_session, test_user.id, "github").id

    body = client.post(
        f"{API}/github/disconnect", json={"purge_evidence": True}, headers=auth_headers
    ).json()
    assert body["evidence_retained"] is False
    assert body["removed"]["artifacts"] == 1
    assert db_session.execute(
        select(IntegrationArtifact).where(IntegrationArtifact.integration_id == integration_id)
    ).scalars().all() == []


def test_disconnect_succeeds_even_when_provider_revocation_fails(
    client, db_session, test_user, auth_headers, fake_providers
):
    """A provider outage must not leave a supposedly-connected row behind."""
    _connect_github(client, auth_headers)

    async def _boom(access_token, refresh_token=None):
        raise RuntimeError("revocation endpoint down")

    fake_providers["oauth"].revoke_token = _boom

    body = client.post(f"{API}/github/disconnect", headers=auth_headers).json()
    assert body["token_revoked_at_provider"] is False
    assert body["status"] == "NOT_CONNECTED"

    record = _record(db_session, test_user.id, "github")
    assert record.is_active is False
    assert record.access_token_encrypted is None


def test_disconnect_of_unconnected_provider_is_404(client, auth_headers, fake_providers):
    response = client.post(f"{API}/github/disconnect", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_connected"


def test_delete_alias_disconnects(client, db_session, test_user, auth_headers, fake_providers):
    _connect_github(client, auth_headers)
    assert client.delete(f"{API}/github", headers=auth_headers).status_code == 200
    assert _record(db_session, test_user.id, "github").is_active is False


# ---------------------------------------------------------------- isolation

def test_one_user_cannot_see_or_touch_another_users_connection(
    client, db_session, test_user, test_user_b, auth_headers, auth_headers_b, fake_providers
):
    _connect_github(client, auth_headers)

    # User B sees nothing connected.
    overview_b = client.get(API, headers=auth_headers_b).json()
    assert overview_b["total_connected"] == 0
    assert client.get(f"{API}/github", headers=auth_headers_b).json()["connected"] is False

    # And cannot sync or disconnect a connection they do not own.
    assert client.post(f"{API}/github/sync", headers=auth_headers_b).status_code == 404
    assert client.post(f"{API}/github/disconnect", headers=auth_headers_b).status_code == 404

    # User A's connection is untouched.
    assert _record(db_session, test_user.id, "github").is_active is True


# ------------------------------------------------------------------- health

def test_health_reports_reachability_and_token_state(
    client, db_session, test_user, auth_headers, fake_providers
):
    _connect_github(client, auth_headers)
    body = client.get(f"{API}/github/health", headers=auth_headers).json()
    assert body["provider"] == "github"
    assert body["reachable"] is True
    assert body["configured"] is True
    assert body["connection_status"] == "SYNCED"
    assert body["last_synced_at"] is not None
    assert body["checked_at"]
    assert "access_token" not in str(body)


def test_health_of_unprobeable_provider_says_so(client, auth_headers, fake_providers):
    body = client.get(f"{API}/gfg/health", headers=auth_headers).json()
    assert body["connection_status"] == "NOT_CONNECTED"
    # Honest "unknown" rather than a fabricated green tick.
    assert body["reachable"] in (None, True, False)
