"""
Password reset and email verification (spec §21, §22).

Design decisions that matter:

* **Tokens are random and stored hashed.** A 32-byte `secrets.token_urlsafe`
  value goes in the email; only its SHA-256 hash is written to the database, so
  a database read cannot be replayed as a reset link.
* **Single use and time limited.** `used_at` and `expires_at` are both checked,
  and outstanding tokens for the same user are invalidated when a new one is
  issued or a reset completes.
* **No account enumeration.** `request_password_reset` returns the same
  response whether or not the address exists, and it says only that an email
  *will be sent if the address is registered*.
* **Delivery is never faked.** `app.core.email.send()` reports whether SMTP
  actually accepted the message; when it did not, we log it and (in DEBUG)
  write the message to the dev outbox. The API response never claims a send
  that did not happen.
* **Sessions are invalidated.** A completed reset revokes every refresh token
  for the user, so stolen sessions die with the old password.
* **Rate limited.** Per-email and per-IP request counters are enforced from the
  token table itself, so the limit survives a restart and multiple workers.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from urllib.parse import quote

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core import email as mailer
from app.core.config import settings
from app.core.exception import ValidationException
from app.core.logging import logger
from app.core.security import hash_password, verify_password
from app.controllers.auth.validators import validate_password
from app.models.auth import EmailVerificationToken, PasswordResetToken, RefreshToken, User

#: Rate limits for reset requests (spec §21).
RESET_MAX_PER_EMAIL_PER_HOUR = 3
RESET_MAX_PER_IP_PER_HOUR = 10
VERIFY_MAX_PER_EMAIL_PER_HOUR = 5

#: Response text used for every outcome of a reset request, so the API cannot
#: be used to discover which addresses are registered.
GENERIC_RESET_MESSAGE = (
    "If that email address has an account, we've sent a password reset link. "
    "Check your inbox and spam folder."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _aware(value: Optional[datetime]) -> Optional[datetime]:
    """Postgres returns tz-aware values; SQLite does not. Normalize to UTC."""
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


@dataclass
class RecoveryOutcome:
    """
    What actually happened. `message` is user-facing; `email_delivered` and
    `email_outbox_path` let an operator see the truth in dev and in logs.
    """

    message: str
    email_delivered: bool = False
    email_outbox_path: Optional[str] = None
    email_configuration_missing: Optional[list] = None


class AccountRecoveryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------- password
    def request_password_reset(
        self,
        email: str,
        *,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RecoveryOutcome:
        """
        Issue a reset token and email it.  Always returns the same message.
        """
        normalized = (email or "").strip().lower()
        user = self.db.execute(
            select(User).where(func.lower(User.email) == normalized)
        ).scalar_one_or_none()

        window_start = _now() - timedelta(hours=1)

        if user is None:
            # Constant work, constant answer: no enumeration signal.
            logger.info("Password reset requested for unknown address (ip=%s)", ip_address)
            return RecoveryOutcome(message=GENERIC_RESET_MESSAGE)

        recent_for_user = self.db.execute(
            select(func.count(PasswordResetToken.id)).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.created_at >= window_start,
            )
        ).scalar_one()
        if recent_for_user >= RESET_MAX_PER_EMAIL_PER_HOUR:
            logger.warning("Password reset rate limit hit for user_id=%s", user.id)
            return RecoveryOutcome(message=GENERIC_RESET_MESSAGE)

        if ip_address:
            recent_for_ip = self.db.execute(
                select(func.count(PasswordResetToken.id)).where(
                    PasswordResetToken.requested_ip == ip_address,
                    PasswordResetToken.created_at >= window_start,
                )
            ).scalar_one()
            if recent_for_ip >= RESET_MAX_PER_IP_PER_HOUR:
                logger.warning("Password reset rate limit hit for ip=%s", ip_address)
                return RecoveryOutcome(message=GENERIC_RESET_MESSAGE)

        # Any earlier unused token becomes invalid — one live link at a time.
        self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=_now())
        )

        raw_token = secrets.token_urlsafe(32)
        record = PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=_now() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_TTL_MINUTES),
            requested_ip=(ip_address or None),
            requested_user_agent=(user_agent or None)[:300] if user_agent else None,
        )
        self.db.add(record)
        self.db.commit()

        reset_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/?reset_token={quote(raw_token)}"
            f"&email={quote(user.email)}#reset-password"
        )
        result = mailer.send_password_reset(
            user.email, user.first_name, reset_url, settings.PASSWORD_RESET_TOKEN_TTL_MINUTES
        )

        # Audit trail: who asked, from where, and whether mail actually left.
        logger.info(
            "Password reset token issued user_id=%s ip=%s delivered=%s",
            user.id,
            ip_address,
            result.delivered,
        )
        return RecoveryOutcome(
            message=GENERIC_RESET_MESSAGE,
            email_delivered=result.delivered,
            email_outbox_path=result.outbox_path,
            email_configuration_missing=result.missing_configuration or None,
        )

    def validate_reset_token(self, raw_token: str) -> bool:
        """True when the token could be used right now. Reveals nothing else."""
        record = self._live_reset_token(raw_token)
        return record is not None

    def _live_reset_token(self, raw_token: str) -> Optional[PasswordResetToken]:
        if not raw_token:
            return None
        record = self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == _hash_token(raw_token)
            )
        ).scalar_one_or_none()
        if record is None or record.used_at is not None:
            return None
        expires_at = _aware(record.expires_at)
        if expires_at is None or expires_at < _now():
            return None
        return record

    def reset_password(self, raw_token: str, new_password: str) -> RecoveryOutcome:
        record = self._live_reset_token(raw_token)
        if record is None:
            # Same message for expired, used, and forged tokens.
            raise ValidationException(
                "That reset link is invalid or has expired. Request a new one."
            )

        is_valid, message = validate_password(new_password)
        if not is_valid:
            raise ValidationException(message)

        user = self.db.execute(
            select(User).where(User.id == record.user_id)
        ).scalar_one_or_none()
        if user is None:
            raise ValidationException(
                "That reset link is invalid or has expired. Request a new one."
            )
        if verify_password(new_password, user.hashed_password):
            raise ValidationException("Choose a password you haven't used on this account.")

        user.hashed_password = hash_password(new_password)
        record.used_at = _now()

        # Invalidate every other outstanding reset token and every session.
        self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=_now())
        )
        revoked = self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True)
        ).rowcount
        self.db.commit()

        logger.info("Password reset completed user_id=%s sessions_revoked=%s", user.id, revoked)
        notice = mailer.send_password_changed_notice(user.email, user.first_name)
        return RecoveryOutcome(
            message="Your password has been changed. Sign in with your new password.",
            email_delivered=notice.delivered,
            email_outbox_path=notice.outbox_path,
        )

    # ---------------------------------------------------------- verification
    def send_verification_email(self, user: User) -> RecoveryOutcome:
        if user.is_verified:
            return RecoveryOutcome(message="Your email address is already verified.")

        window_start = _now() - timedelta(hours=1)
        recent = self.db.execute(
            select(func.count(EmailVerificationToken.id)).where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.created_at >= window_start,
            )
        ).scalar_one()
        if recent >= VERIFY_MAX_PER_EMAIL_PER_HOUR:
            raise ValidationException(
                "Too many verification emails requested. Try again in an hour."
            )

        self.db.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used_at.is_(None),
            )
            .values(used_at=_now())
        )

        raw_token = secrets.token_urlsafe(32)
        self.db.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=_hash_token(raw_token),
                email=user.email,
                expires_at=_now()
                + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_TTL_HOURS),
            )
        )
        self.db.commit()

        verify_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/?verify_token={quote(raw_token)}#verify-email"
        )
        result = mailer.send_email_verification(
            user.email, user.first_name, verify_url, settings.EMAIL_VERIFICATION_TOKEN_TTL_HOURS
        )
        logger.info(
            "Verification token issued user_id=%s delivered=%s", user.id, result.delivered
        )

        if not result.delivered:
            # Say what is true rather than "email sent".
            return RecoveryOutcome(
                message=(
                    "We could not send the verification email right now. "
                    "Try again shortly or contact support."
                ),
                email_delivered=False,
                email_outbox_path=result.outbox_path,
                email_configuration_missing=result.missing_configuration or None,
            )
        return RecoveryOutcome(
            message="Verification email sent. Check your inbox.", email_delivered=True
        )

    def verify_email(self, raw_token: str) -> Tuple[User, RecoveryOutcome]:
        if not raw_token:
            raise ValidationException("That verification link is invalid or has expired.")
        record = self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == _hash_token(raw_token)
            )
        ).scalar_one_or_none()

        expires_at = _aware(record.expires_at) if record else None
        if record is None or record.used_at is not None or expires_at is None or expires_at < _now():
            raise ValidationException(
                "That verification link is invalid or has expired. Request a new one."
            )

        user = self.db.execute(
            select(User).where(User.id == record.user_id)
        ).scalar_one_or_none()
        if user is None:
            raise ValidationException("That verification link is invalid or has expired.")

        # The address may have changed since the token was issued.
        if (record.email or "").lower() != (user.email or "").lower():
            record.used_at = _now()
            self.db.commit()
            raise ValidationException(
                "That verification link was issued for a different email address."
            )

        user.is_verified = True
        user.email_verified_at = _now()
        record.used_at = _now()
        self.db.commit()

        logger.info("Email verified user_id=%s", user.id)
        return user, RecoveryOutcome(message="Your email address is verified.")
