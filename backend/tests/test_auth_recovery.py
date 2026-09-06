"""
Password reset and email verification (spec §21, §22).

The reset token only ever exists in the email body, so these tests intercept
`app.core.email.send` to read the link the user would receive. That is also the
assertion that matters most: the token is not in any API response, and the
database only holds its hash.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import List
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import select

from app.core import email as mailer
from app.core.config import settings
from app.core.security import verify_password
from app.models.auth import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
)

AUTH = "/api/v1/auth"
NEW_PASSWORD = "N3w!Str0ngPassw0rd"


@pytest.fixture
def outbox(monkeypatch) -> List[dict]:
    """
    Capture every send attempt instead of touching SMTP. `delivered=True` is
    reported so the "we could not send it" branches are not what gets tested
    here — they have their own test.
    """
    sent: List[dict] = []

    def _capture(to, subject, text_body, html_body=None):
        sent.append(
            {"to": to, "subject": subject, "text": text_body, "html": html_body or ""}
        )
        return mailer.DeliveryResult(delivered=True)

    monkeypatch.setattr(mailer, "send", _capture)
    return sent


def _link_token(message: dict, param: str) -> str:
    """Pull the single-use token out of the emailed URL."""
    for word in message["text"].split():
        if param in word:
            return parse_qs(urlparse(word.strip().rstrip(".")).query)[param][0]
    raise AssertionError(f"no {param} link in email: {message['text']!r}")


def _request_reset(client, email="alice@example.com"):
    return client.post(f"{AUTH}/forgot-password", json={"email": email})


# ------------------------------------------------------------ reset: issuing

def test_reset_request_emails_a_token_that_is_stored_only_as_a_hash(
    client, db_session, test_user, outbox
):
    response = _request_reset(client)
    assert response.status_code == 200
    assert response.json()["email_delivered"] is True

    assert len(outbox) == 1
    raw_token = _link_token(outbox[0], "reset_token")
    assert outbox[0]["to"] == test_user.email

    # The token reached the user's inbox and nowhere else.
    assert raw_token not in response.text

    record = db_session.execute(select(PasswordResetToken)).scalars().one()
    assert record.user_id == test_user.id
    assert record.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()
    assert record.token_hash != raw_token
    assert record.used_at is None
    # A stored hash cannot be replayed as a link.
    assert raw_token not in str(record.__dict__)

    # And it expires.
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    assert expires_at > datetime.now(timezone.utc)
    assert expires_at <= datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_TTL_MINUTES + 1
    )


def test_reset_request_for_unknown_address_is_indistinguishable(
    client, db_session, test_user, outbox
):
    """No account enumeration: same status, same body, and no email sent."""
    known = _request_reset(client, "alice@example.com")
    unknown = _request_reset(client, "nobody@example.com")

    assert known.status_code == unknown.status_code == 200
    assert known.json()["message"] == unknown.json()["message"]
    # Only the real address received mail.
    assert [m["to"] for m in outbox] == ["alice@example.com"]
    assert db_session.execute(select(PasswordResetToken)).scalars().all().__len__() == 1


def test_reset_request_is_case_insensitive_on_email(client, test_user, outbox):
    assert _request_reset(client, "ALICE@Example.com").status_code == 200
    assert len(outbox) == 1


def test_issuing_a_new_token_invalidates_the_previous_one(
    client, db_session, test_user, outbox
):
    _request_reset(client)
    first_token = _link_token(outbox[0], "reset_token")
    _request_reset(client)
    second_token = _link_token(outbox[1], "reset_token")
    assert first_token != second_token

    # Only one live link at a time.
    stale = client.get(f"{AUTH}/reset-password/validate", params={"token": first_token})
    assert stale.json()["valid"] is False
    live = client.get(f"{AUTH}/reset-password/validate", params={"token": second_token})
    assert live.json()["valid"] is True


def test_reset_requests_are_rate_limited_per_email(client, db_session, test_user, outbox):
    from app.controllers.auth.account_recovery import RESET_MAX_PER_EMAIL_PER_HOUR

    for _ in range(RESET_MAX_PER_EMAIL_PER_HOUR):
        assert _request_reset(client).status_code == 200
    throttled = _request_reset(client)

    # The limit is silent — it must not become an enumeration oracle either.
    assert throttled.status_code == 200
    assert throttled.json()["message"] == _request_reset(client).json()["message"]
    # No further token issued and no further mail sent.
    assert len(outbox) == RESET_MAX_PER_EMAIL_PER_HOUR
    assert (
        len(db_session.execute(select(PasswordResetToken)).scalars().all())
        == RESET_MAX_PER_EMAIL_PER_HOUR
    )


def test_response_never_leaks_the_outbox_path_outside_debug(
    client, test_user, monkeypatch
):
    monkeypatch.setattr(settings, "DEBUG", False)
    body = _request_reset(client).json()
    # SMTP is unconfigured in tests, so delivery honestly reports False...
    assert body["email_delivered"] is False
    # ...and the dev outbox path (a live reset link on disk) is withheld.
    assert body["email_outbox_path"] is None


# ------------------------------------------------------------ reset: using

def test_reset_changes_the_password_consumes_the_token_and_kills_sessions(
    client, db_session, test_user, outbox
):
    # An existing session that must not survive the reset.
    session_token = RefreshToken(
        user_id=test_user.id,
        token="refresh-token-1",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_revoked=False,
    )
    db_session.add(session_token)
    db_session.commit()

    _request_reset(client)
    raw_token = _link_token(outbox[0], "reset_token")

    response = client.post(
        f"{AUTH}/reset-password", json={"token": raw_token, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 200

    db_session.refresh(test_user)
    assert verify_password(NEW_PASSWORD, test_user.hashed_password)
    assert not verify_password("Str0ng!Passw0rd", test_user.hashed_password)

    record = db_session.execute(select(PasswordResetToken)).scalars().one()
    assert record.used_at is not None

    db_session.refresh(session_token)
    assert session_token.is_revoked is True

    # The new password actually works and the old one does not.
    assert client.post(
        f"{AUTH}/login", json={"email": test_user.email, "password": NEW_PASSWORD}
    ).status_code == 200
    assert client.post(
        f"{AUTH}/login", json={"email": test_user.email, "password": "Str0ng!Passw0rd"}
    ).status_code in (400, 401)


def test_reset_token_is_single_use(client, db_session, test_user, outbox):
    _request_reset(client)
    raw_token = _link_token(outbox[0], "reset_token")

    first = client.post(
        f"{AUTH}/reset-password", json={"token": raw_token, "new_password": NEW_PASSWORD}
    )
    assert first.status_code == 200

    replay = client.post(
        f"{AUTH}/reset-password",
        json={"token": raw_token, "new_password": "An0ther!Passw0rd"},
    )
    assert replay.status_code in (400, 422)

    db_session.refresh(test_user)
    # The replay did not take effect.
    assert verify_password(NEW_PASSWORD, test_user.hashed_password)


def test_expired_token_is_refused(client, db_session, test_user, outbox):
    _request_reset(client)
    raw_token = _link_token(outbox[0], "reset_token")

    record = db_session.execute(select(PasswordResetToken)).scalars().one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    assert client.get(
        f"{AUTH}/reset-password/validate", params={"token": raw_token}
    ).json()["valid"] is False
    assert client.post(
        f"{AUTH}/reset-password", json={"token": raw_token, "new_password": NEW_PASSWORD}
    ).status_code in (400, 422)

    db_session.refresh(test_user)
    assert verify_password("Str0ng!Passw0rd", test_user.hashed_password)


def test_forged_token_is_refused_with_the_same_message_as_an_expired_one(
    client, db_session, test_user, outbox
):
    forged = client.post(
        f"{AUTH}/reset-password",
        json={"token": "f" * 43, "new_password": NEW_PASSWORD},
    )
    assert forged.status_code in (400, 422)

    _request_reset(client)
    record = db_session.execute(select(PasswordResetToken)).scalars().one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    expired = client.post(
        f"{AUTH}/reset-password",
        json={"token": _link_token(outbox[0], "reset_token"), "new_password": NEW_PASSWORD},
    )
    # An attacker cannot tell "no such token" from "expired token".
    assert forged.status_code == expired.status_code
    assert forged.json()["error"]["message"] == expired.json()["error"]["message"]


def test_reset_enforces_the_password_policy(client, db_session, test_user, outbox):
    _request_reset(client)
    raw_token = _link_token(outbox[0], "reset_token")

    weak = client.post(
        f"{AUTH}/reset-password", json={"token": raw_token, "new_password": "password"}
    )
    assert weak.status_code in (400, 422)

    db_session.refresh(test_user)
    assert verify_password("Str0ng!Passw0rd", test_user.hashed_password)
    # A rejected attempt must not have burned the token.
    assert client.get(
        f"{AUTH}/reset-password/validate", params={"token": raw_token}
    ).json()["valid"] is True


def test_reset_rejects_reusing_the_current_password(client, db_session, test_user, outbox):
    _request_reset(client)
    raw_token = _link_token(outbox[0], "reset_token")

    response = client.post(
        f"{AUTH}/reset-password",
        json={"token": raw_token, "new_password": "Str0ng!Passw0rd"},
    )
    assert response.status_code in (400, 422)
    db_session.refresh(test_user)
    assert verify_password("Str0ng!Passw0rd", test_user.hashed_password)


def test_validate_endpoint_reveals_nothing_but_usability(client, test_user, outbox):
    body = client.get(
        f"{AUTH}/reset-password/validate", params={"token": "nonexistent-token-value"}
    ).json()
    assert body == {"valid": False}


# ----------------------------------------------------------- verification

def test_verification_email_carries_a_hashed_single_use_token(
    client, db_session, auth_headers, test_user, outbox
):
    test_user.is_verified = False
    db_session.commit()

    response = client.post(f"{AUTH}/send-verification", headers=auth_headers)
    assert response.status_code == 200
    raw_token = _link_token(outbox[0], "verify_token")
    assert raw_token not in response.text

    record = db_session.execute(select(EmailVerificationToken)).scalars().one()
    assert record.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()
    assert record.email == test_user.email

    confirmed = client.post(f"{AUTH}/verify-email", json={"token": raw_token})
    assert confirmed.status_code == 200

    db_session.refresh(test_user)
    assert test_user.is_verified is True
    assert test_user.email_verified_at is not None

    # Single use.
    assert client.post(f"{AUTH}/verify-email", json={"token": raw_token}).status_code in (
        400,
        422,
    )


def test_verification_requires_authentication(client, test_user, outbox):
    assert client.post(f"{AUTH}/send-verification").status_code in (401, 403)
    assert outbox == []


def test_expired_verification_token_is_refused(
    client, db_session, auth_headers, test_user, outbox
):
    test_user.is_verified = False
    db_session.commit()
    client.post(f"{AUTH}/send-verification", headers=auth_headers)
    raw_token = _link_token(outbox[0], "verify_token")

    record = db_session.execute(select(EmailVerificationToken)).scalars().one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.commit()

    assert client.post(f"{AUTH}/verify-email", json={"token": raw_token}).status_code in (
        400,
        422,
    )
    db_session.refresh(test_user)
    assert test_user.is_verified is False


def test_verification_token_issued_for_a_different_address_is_refused(
    client, db_session, auth_headers, test_user, outbox
):
    """Changing the email address must invalidate a link sent to the old one."""
    test_user.is_verified = False
    db_session.commit()
    client.post(f"{AUTH}/send-verification", headers=auth_headers)
    raw_token = _link_token(outbox[0], "verify_token")

    test_user.email = "alice.new@example.com"
    db_session.commit()

    assert client.post(f"{AUTH}/verify-email", json={"token": raw_token}).status_code in (
        400,
        422,
    )
    db_session.refresh(test_user)
    assert test_user.is_verified is False


def test_verification_resend_is_rate_limited(
    client, db_session, auth_headers, test_user, outbox
):
    from app.controllers.auth.account_recovery import VERIFY_MAX_PER_EMAIL_PER_HOUR

    test_user.is_verified = False
    db_session.commit()

    for _ in range(VERIFY_MAX_PER_EMAIL_PER_HOUR):
        assert client.post(f"{AUTH}/send-verification", headers=auth_headers).status_code == 200
    throttled = client.post(f"{AUTH}/send-verification", headers=auth_headers)
    assert throttled.status_code in (400, 422, 429)
    assert len(outbox) == VERIFY_MAX_PER_EMAIL_PER_HOUR


def test_already_verified_account_is_told_so_without_a_new_token(
    client, db_session, auth_headers, test_user, outbox
):
    assert test_user.is_verified is True
    response = client.post(f"{AUTH}/send-verification", headers=auth_headers)
    assert response.status_code == 200
    assert "already verified" in response.json()["message"].lower()
    assert outbox == []
    assert db_session.execute(select(EmailVerificationToken)).scalars().all() == []


def test_undeliverable_verification_email_is_reported_honestly(
    client, db_session, auth_headers, test_user, monkeypatch
):
    """No fake "email sent" when the mail server rejected the message."""
    monkeypatch.setattr(
        mailer,
        "send",
        lambda *a, **k: mailer.DeliveryResult(
            delivered=False, missing_configuration=["SMTP_HOST"], error="smtp_not_configured"
        ),
    )
    test_user.is_verified = False
    db_session.commit()

    body = client.post(f"{AUTH}/send-verification", headers=auth_headers).json()
    assert body["email_delivered"] is False
    assert "could not send" in body["message"].lower()
    db_session.refresh(test_user)
    assert test_user.is_verified is False
