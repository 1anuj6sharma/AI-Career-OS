"""
Outbound transactional email (spec §21, §22).

One rule shapes this module: **the caller is told whether the message was
actually handed to a mail server.**  `send()` returns a `DeliveryResult`, and a
deployment without SMTP configured gets `delivered=False` — never a fake
"email sent" confirmation.

Behaviour by environment:

* SMTP configured → real `smtplib` delivery (SSL or STARTTLS), `delivered=True`
  only after the server accepted the message.
* SMTP not configured and `DEBUG` → the message is written to
  `EMAIL_DEV_OUTBOX` as an .eml file so a developer can open the link, with
  `delivered=False` and `outbox_path` set.
* SMTP not configured and not `DEBUG` → nothing is sent, `delivered=False`,
  and `missing_configuration` names the exact variables to set.
"""
from __future__ import annotations

import smtplib
import ssl
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, formatdate
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.core.logging import logger

#: Variables that must be present for real delivery.
REQUIRED_SETTINGS = ("SMTP_HOST", "EMAIL_FROM")


@dataclass
class DeliveryResult:
    """Truthful outcome of one send attempt."""

    delivered: bool
    #: Set when the message was written to the dev outbox instead of being sent.
    outbox_path: Optional[str] = None
    #: Env vars still required for real delivery.
    missing_configuration: List[str] = field(default_factory=list)
    #: Server-side reason. Never shown to an end user.
    error: Optional[str] = None


def missing_configuration() -> List[str]:
    return [name for name in REQUIRED_SETTINGS if not getattr(settings, name, "")]


def _build_message(to: str, subject: str, text_body: str, html_body: Optional[str]) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.EMAIL_FROM_NAME, settings.EMAIL_FROM or "no-reply@localhost"))
    message["To"] = to
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = f"<{uuid.uuid4()}@ai-career-os>"
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")
    return message


def _write_to_outbox(message: EmailMessage, to: str) -> Optional[str]:
    """Persist the message locally so a dev can still follow the link."""
    try:
        outbox = Path(settings.EMAIL_DEV_OUTBOX)
        outbox.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        safe_to = "".join(c if c.isalnum() or c in "._-@" else "_" for c in to)[:60]
        path = outbox / f"{stamp}-{safe_to}-{uuid.uuid4().hex[:8]}.eml"
        path.write_bytes(bytes(message))
        return str(path)
    except OSError as exc:
        logger.warning("Could not write dev outbox message: %r", exc)
        return None


def send(
    to: str,
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
) -> DeliveryResult:
    """
    Attempt delivery. Returns a truthful result; raises nothing so an auth flow
    is never broken by a mail outage.
    """
    missing = missing_configuration()
    message = _build_message(to, subject, text_body, html_body)

    if missing:
        outbox_path = _write_to_outbox(message, to) if settings.DEBUG else None
        logger.warning(
            "Email to %s NOT sent: missing configuration %s%s",
            to,
            ", ".join(missing),
            f"; written to {outbox_path}" if outbox_path else "",
        )
        return DeliveryResult(
            delivered=False,
            outbox_path=outbox_path,
            missing_configuration=missing,
            error="smtp_not_configured",
        )

    try:
        if settings.SMTP_USE_SSL:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=20
            ) as server:
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
                server.ehlo()
                if settings.SMTP_USE_TLS:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
    except (smtplib.SMTPException, OSError, ssl.SSLError) as exc:
        # Log the technical reason; the caller shows a generic message.
        logger.error("Email delivery to %s failed: %r", to, exc)
        return DeliveryResult(delivered=False, error=repr(exc)[:300])

    logger.info("Email delivered to %s: %s", to, subject)
    return DeliveryResult(delivered=True)


# --------------------------------------------------------------------------- #
# Templates
# --------------------------------------------------------------------------- #

_WRAPPER = """\
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            max-width:520px;margin:0 auto;color:#14161a;line-height:1.55">
  <h2 style="font-size:19px;margin:0 0 14px">{heading}</h2>
  {body}
  <p style="margin:28px 0 0;padding-top:16px;border-top:1px solid #e6e8ec;
            font-size:12px;color:#6b7280">
    {footer}
  </p>
</div>
"""

_BUTTON = """\
<p style="margin:22px 0">
  <a href="{url}" style="display:inline-block;background:#4f46e5;color:#fff;
     text-decoration:none;padding:11px 20px;border-radius:8px;font-weight:600">{label}</a>
</p>
<p style="font-size:12px;color:#6b7280;word-break:break-all;margin:0">
  Or paste this link into your browser:<br>{url}
</p>
"""


def send_password_reset(to: str, first_name: str, reset_url: str, ttl_minutes: int) -> DeliveryResult:
    text = (
        f"Hi {first_name},\n\n"
        f"Use this link to set a new AI Career OS password:\n{reset_url}\n\n"
        f"The link works once and expires in {ttl_minutes} minutes.\n"
        "If you did not request a password reset, you can ignore this email — "
        "your password has not changed.\n"
    )
    html = _WRAPPER.format(
        heading="Reset your password",
        body=(
            f"<p style='margin:0'>Hi {first_name}, use the button below to set a new password.</p>"
            + _BUTTON.format(url=reset_url, label="Set a new password")
        ),
        footer=(
            f"This link works once and expires in {ttl_minutes} minutes. "
            "If you did not request a reset, ignore this email — your password has not changed."
        ),
    )
    return send(to, "Reset your AI Career OS password", text, html)


def send_email_verification(to: str, first_name: str, verify_url: str, ttl_hours: int) -> DeliveryResult:
    text = (
        f"Hi {first_name},\n\n"
        f"Confirm your email address for AI Career OS:\n{verify_url}\n\n"
        f"The link works once and expires in {ttl_hours} hours.\n"
    )
    html = _WRAPPER.format(
        heading="Confirm your email address",
        body=(
            f"<p style='margin:0'>Hi {first_name}, confirm this address to finish setting up your account.</p>"
            + _BUTTON.format(url=verify_url, label="Confirm email address")
        ),
        footer=f"This link works once and expires in {ttl_hours} hours.",
    )
    return send(to, "Confirm your AI Career OS email address", text, html)


def send_password_changed_notice(to: str, first_name: str) -> DeliveryResult:
    text = (
        f"Hi {first_name},\n\n"
        "Your AI Career OS password was just changed and all other sessions were signed out.\n"
        "If this wasn't you, reset your password immediately.\n"
    )
    html = _WRAPPER.format(
        heading="Your password was changed",
        body=(
            "<p style='margin:0'>Your password was just changed and every other session "
            "was signed out.</p>"
        ),
        footer="If this wasn't you, reset your password immediately.",
    )
    return send(to, "Your AI Career OS password was changed", text, html)
