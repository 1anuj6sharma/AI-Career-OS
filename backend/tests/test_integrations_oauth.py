"""
Connected Accounts — OAuth lifecycle (spec §30).

Covers connection initiation, the callback, invalid/replayed/expired state,
token exchange and refresh, profile fetch, and identity verification.
External providers are faked; no network call is made.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import select

from app.controllers.integrations.crypto import get_cipher
from app.controllers.integrations.providers.base import (
    ProviderAuthExpired,
    ProviderError,
)
from app.core.config import settings
from app.models.integrations import (
    IntegrationArtifact,
    IntegrationMetric,
    IntegrationSyncRun,
    OAuthAuthorizationState,
    UserIntegration,
)

API = "/api/v1/integrations"


def _naive_utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _state_row(db_session, provider="github") -> OAuthAuthorizationState:
    return db_session.execute(
        select(OAuthAuthorizationState).where(OAuthAuthorizationState.provider == provider)
    ).scalars().first()


def _record(db_session, user_id, provider="github") -> UserIntegration:
    return db_session.execute(
        select(UserIntegration).where(
            UserIntegration.user_id == user_id, UserIntegration.provider == provider
        )
    ).scalar_one_or_none()


# --------------------------------------------------------------- authorization

def test_connect_returns_authorization_url_and_persists_single_use_state(
    client, db_session, test_user, auth_headers, fake_providers
):
    response = client.get(f"{API}/github/connect", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()

    # Both keys are populated: the frontend contract uses `url`.
    assert body["authorization_url"] == body["url"]
    assert body["provider"] == "github"
    assert body["expires_in_seconds"] == settings.OAUTH_STATE_TTL_SECONDS

    query = parse_qs(urlparse(body["url"]).query)
    state = query["state"][0]
    # PKCE is used because the fake connector declares support for it.
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"][0]

    row = _state_row(db_session)
    assert row.state == state
    assert row.consumed_at is None
    assert row.expires_at > _naive_utcnow()
    # The verifier is a short-lived secret and is stored encrypted.
    assert row.code_verifier_encrypted
    assert get_cipher().decrypt(row.code_verifier_encrypted) not in (None, "")
    assert row.redirect_uri.endswith("/api/v1/integrations/github/callback")

    # The account shows CONNECTING, not CONNECTED — nothing is authenticated yet.
    assert _record(db_session, test_user.id).connection_status == "CONNECTING"


def test_connect_requires_authentication(client, fake_providers):
    assert client.get(f"{API}/github/connect").status_code in (401, 403)


def test_connect_rejects_unconfigured_provider(client, auth_headers, fake_providers):
    fake_providers["oauth"].configured = False
    response = client.get(f"{API}/github/connect", headers=auth_headers)
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["code"] == "configuration_required"
    # The missing variable names are logged server-side, not returned.
    assert "GITHUB_CLIENT_SECRET" not in response.text


def test_connect_rejects_non_oauth_provider(client, auth_headers, fake_providers):
    response = client.get(f"{API}/leetcode/connect", headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "oauth_not_supported"


def test_unknown_provider_is_404(client, auth_headers, fake_providers):
    response = client.get(f"{API}/myspace", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "unknown_provider"


# -------------------------------------------------------------------- callback

def _begin(client, auth_headers) -> str:
    body = client.get(f"{API}/github/connect", headers=auth_headers).json()
    return parse_qs(urlparse(body["url"]).query)["state"][0]


def test_callback_completes_connection_and_runs_initial_sync(
    client, db_session, test_user, auth_headers, fake_providers
):
    state = _begin(client, auth_headers)
    oauth = fake_providers["oauth"]

    response = client.get(
        f"{API}/github/callback?code=auth-code-1&state={state}", follow_redirects=False
    )
    assert response.status_code in (302, 307)
    location = response.headers["location"]
    assert location.startswith(settings.FRONTEND_URL)
    assert "connected=1" in location
    # No token, no provider payload, no exception text in the redirect.
    assert "gho_access" not in location
    assert "ghr_refresh" not in location

    # The PKCE verifier generated at /connect was forwarded to the token endpoint.
    assert oauth.exchange_calls[0]["code"] == "auth-code-1"
    assert oauth.exchange_calls[0]["code_verifier"]
    assert oauth.exchange_calls[0]["redirect_uri"].endswith("/github/callback")

    record = _record(db_session, test_user.id)
    assert record.is_active is True
    assert record.provider_account_id == "5551212"
    assert record.provider_username == "octodev"
    assert record.email == "octo@example.com"
    assert record.scopes == "read:user user:email"
    # Real timestamps, not placeholders.
    assert record.last_connected_at is not None
    assert record.last_synced_at is not None
    assert record.connection_status == "SYNCED"

    # Tokens are stored as ciphertext and decrypt back to the issued values.
    assert record.access_token_encrypted != oauth.access_token
    assert get_cipher().decrypt(record.access_token_encrypted) == oauth.access_token
    assert get_cipher().decrypt(record.refresh_token_encrypted) == "ghr_refresh_1"

    # The initial sync actually wrote normalized rows.
    metrics = {
        m.metric_key: m.metric_value
        for m in db_session.execute(
            select(IntegrationMetric).where(IntegrationMetric.integration_id == record.id)
        ).scalars()
    }
    assert metrics["total_stars"] == 13
    assert metrics["repos_count"] == 7
    artifacts = db_session.execute(
        select(IntegrationArtifact).where(IntegrationArtifact.integration_id == record.id)
    ).scalars().all()
    assert [a.external_id for a in artifacts] == ["octodev/career-os"]

    run = db_session.execute(
        select(IntegrationSyncRun).where(IntegrationSyncRun.integration_id == record.id)
    ).scalars().one()
    assert run.trigger == "initial"
    assert run.status == "SYNCED"
    assert run.duration_ms is not None


def test_callback_state_is_single_use(client, db_session, auth_headers, fake_providers):
    state = _begin(client, auth_headers)
    first = client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)
    assert "connected=1" in first.headers["location"]

    replay = client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)
    assert "error=state_replayed" in replay.headers["location"]
    assert "connected=1" not in replay.headers["location"]


def test_callback_rejects_forged_and_missing_state(client, auth_headers, fake_providers):
    forged = client.get(
        f"{API}/github/callback?code=c1&state=not-a-real-state", follow_redirects=False
    )
    assert "error=invalid_state" in forged.headers["location"]

    missing = client.get(f"{API}/github/callback?code=c1", follow_redirects=False)
    assert "error=invalid_state" in missing.headers["location"]

    # A forged state must not create or authenticate an account.
    assert fake_providers["oauth"].exchange_calls == []


def test_callback_rejects_state_issued_for_another_provider(
    client, db_session, auth_headers, fake_providers
):
    state = _begin(client, auth_headers)
    response = client.get(
        f"{API}/google/callback?code=c1&state={state}", follow_redirects=False
    )
    assert "error=invalid_state" in response.headers["location"]
    assert fake_providers["oauth"].exchange_calls == []


def test_callback_rejects_expired_state(client, db_session, auth_headers, fake_providers):
    state = _begin(client, auth_headers)
    row = _state_row(db_session)
    row.expires_at = _naive_utcnow() - timedelta(seconds=1)
    db_session.commit()

    response = client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)
    assert "error=state_expired" in response.headers["location"]
    assert fake_providers["oauth"].exchange_calls == []


def test_callback_handles_user_denial(client, db_session, test_user, auth_headers, fake_providers):
    _begin(client, auth_headers)
    response = client.get(
        f"{API}/github/callback?error=access_denied&error_description=user+said+no",
        follow_redirects=False,
    )
    assert "error=oauth_denied" in response.headers["location"]
    # The provider's description text is not echoed to the browser.
    assert "user+said+no" not in response.headers["location"]
    assert _record(db_session, test_user.id).is_active is False


def test_callback_without_code_is_reported(client, auth_headers, fake_providers):
    _begin(client, auth_headers)
    response = client.get(f"{API}/github/callback?state=x", follow_redirects=False)
    assert "error=missing_code" in response.headers["location"]


def test_callback_token_exchange_failure_does_not_connect(
    client, db_session, test_user, auth_headers, fake_providers
):
    state = _begin(client, auth_headers)
    fake_providers["oauth"].exchange_error = ProviderError(
        "GitHub did not issue an access token.",
        code="token_exchange_failed",
        detail="bad_verification_code from provider",
    )

    response = client.get(f"{API}/github/callback?code=stale&state={state}", follow_redirects=False)
    location = response.headers["location"]
    assert "error=token_exchange_failed" in location
    # Server-side detail must never reach the browser.
    assert "bad_verification_code" not in location

    record = _record(db_session, test_user.id)
    assert record.is_active is False
    assert record.connection_status != "CONNECTED"
    assert record.access_token_encrypted is None


def test_callback_requires_verified_identity(
    client, db_session, test_user, auth_headers, fake_providers
):
    """A provider response with no account id must not produce a connection."""
    state = _begin(client, auth_headers)
    fake_providers["oauth"].profile_override = {
        "provider_username": "octodev",
        "provider_account_id": None,
    }

    response = client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)
    assert "error=identity_verification_failed" in response.headers["location"]

    record = _record(db_session, test_user.id)
    assert record.is_active is False
    assert record.provider_account_id is None


# ------------------------------------------------------------- token refresh

def test_expiring_access_token_is_refreshed_before_use(
    client, db_session, test_user, auth_headers, fake_providers
):
    oauth = fake_providers["oauth"]
    oauth.expires_in = 30  # inside the 5-minute refresh margin
    state = _begin(client, auth_headers)
    client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)

    # The initial sync had to refresh first, and used the refreshed token.
    assert oauth.refresh_calls == ["ghr_refresh_1"]
    assert oauth.telemetry_calls == [oauth.refreshed_access_token]

    record = _record(db_session, test_user.id)
    # The rotated refresh token replaced the old one, still encrypted.
    assert get_cipher().decrypt(record.refresh_token_encrypted) == "ghr_refresh_2"
    assert get_cipher().decrypt(record.access_token_encrypted) == oauth.refreshed_access_token
    assert record.token_expires_at > _naive_utcnow()


def test_failed_refresh_requires_reauth_and_clears_access_token(
    client, db_session, test_user, auth_headers, fake_providers
):
    oauth = fake_providers["oauth"]
    state = _begin(client, auth_headers)
    client.get(f"{API}/github/callback?code=c1&state={state}", follow_redirects=False)

    record = _record(db_session, test_user.id)
    record.token_expires_at = _naive_utcnow() - timedelta(minutes=1)
    db_session.commit()
    oauth.refresh_response = ProviderAuthExpired(
        "GitHub authorization expired. Reconnect required.", detail="refresh token revoked"
    )

    response = client.post(
        f"{API}/github/sync", json={"force": True}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REAUTH_REQUIRED"
    assert body["requires_reauth"] is True
    assert "revoked" not in response.text  # server-side detail stays server-side

    db_session.refresh(record)
    assert record.connection_status == "REAUTH_REQUIRED"
    assert record.access_token_encrypted is None
    assert record.token_expires_at is None
