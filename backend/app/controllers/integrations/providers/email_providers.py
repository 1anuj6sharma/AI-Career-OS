"""
Mailbox connectors — Gmail (Google) and Outlook (Microsoft Graph).

Both are OAuth 2.0 with PKCE and read-only mail scopes.  Neither ever asks for
the user's mail password (spec §12/§13), and no code path in this module can
modify or delete mail: only GET requests are issued.

`EmailConnector` holds everything the two share — the search window, message
scanning, classification via `job_mail`, and the sanitized summary — so each
subclass only supplies its own OAuth endpoints and message-listing calls.
"""
from __future__ import annotations

import base64
import logging
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr, parsedate_to_datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings

from . import http, job_mail
from .base import (
    AuthMethod,
    Capability,
    OAuthProvider,
    ProviderDescriptor,
    ProviderError,
)
from .job_mail import MailMessage

logger = logging.getLogger(__name__)

#: How far back a sync looks, and how many messages it will examine. Bounded so
#: a sync cannot hammer the provider or run unbounded (spec §17).
LOOKBACK_DAYS = 90
MAX_MESSAGES = 150


class EmailConnector(OAuthProvider):
    """Shared behaviour for mailbox providers."""

    @property
    def mailbox_url(self) -> str:
        """Where [Open] should take the user (their webmail, not a profile)."""
        raise NotImplementedError

    async def list_recent_messages(self, access_token: str, since: datetime) -> List[MailMessage]:
        """Provider-specific: return message envelopes newer than `since`."""
        raise NotImplementedError

    def get_external_url(self, account: Dict[str, Any]) -> Optional[str]:  # noqa: ARG002
        return self.mailbox_url

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        """
        Scan the recent mailbox window, classify career mail, and return a
        summary plus the normalized events for the Application Pipeline.
        Read-only throughout.
        """
        since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
        messages = await self.list_recent_messages(access_token, since)
        events = []
        for message in messages:
            event = job_mail.classify(message, source=self.provider_name)
            if event:
                events.append(event)

        return {
            "email": identifier,
            "messages_scanned": len(messages),
            "scan_window_days": LOOKBACK_DAYS,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            **job_mail.summarize(events),
            # Consumed by the evidence pipeline, then dropped from API output.
            "job_events": [event.to_dict() for event in events],
            "data_source": f"{self.descriptor.display_name} read-only API",
        }


# --------------------------------------------------------------------------- #
# Gmail
# --------------------------------------------------------------------------- #

GOOGLE_SCOPES = (
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
)

GOOGLE_DESCRIPTOR = ProviderDescriptor(
    name="google",
    display_name="Gmail",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset(
        {
            Capability.IDENTITY,
            Capability.PROFILE,
            Capability.EMAIL_READ,
            Capability.ACTIVITY,
            Capability.TOKEN_REFRESH,
            Capability.TOKEN_REVOKE,
        }
    ),
    scopes=GOOGLE_SCOPES,
    allowed_url_hosts=("mail.google.com", "google.com"),
    docs_url="https://developers.google.com/gmail/api/auth/scopes",
    limitation_note=(
        "Read-only Gmail access. We scan recent mail for job-application activity "
        "and never send, modify or delete anything."
    ),
)


class GoogleProvider(EmailConnector):
    supports_pkce = True

    @property
    def descriptor(self) -> ProviderDescriptor:
        return GOOGLE_DESCRIPTOR

    @property
    def mailbox_url(self) -> str:
        return "https://mail.google.com/"

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def missing_configuration(self) -> List[str]:
        missing = []
        if not settings.GOOGLE_CLIENT_ID:
            missing.append("GOOGLE_CLIENT_ID")
        if not settings.GOOGLE_CLIENT_SECRET:
            missing.append("GOOGLE_CLIENT_SECRET")
        return missing

    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        payload = await http.request_json(
            "Google", "POST", "https://oauth2.googleapis.com/token", action="token exchange", data=data
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Google did not issue an access token. Try connecting again.",
                detail=f"Google token response: {payload.get('error')} {payload.get('error_description')}",
                code="token_exchange_failed",
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token"),
            "expires_in": payload.get("expires_in"),
            "scope": payload.get("scope"),
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = await http.request_json(
            "Google",
            "POST",
            "https://oauth2.googleapis.com/token",
            action="token refresh",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Gmail authorization expired. Reconnect required.",
                detail=f"Google refresh response: {payload.get('error_description')}",
                code="reauth_required",
                requires_reauth=True,
            )
        return {
            "access_token": payload["access_token"],
            # Google does not reissue the refresh token on refresh.
            "refresh_token": payload.get("refresh_token") or refresh_token,
            "expires_in": payload.get("expires_in"),
        }

    async def revoke_token(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        target = refresh_token or access_token
        try:
            async with http.client() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    data={"token": target},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            return response.status_code == 200
        except Exception:  # noqa: BLE001 - best effort on disconnect
            return False

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        user = await http.request_json(
            "Google",
            "GET",
            "https://openidconnect.googleapis.com/v1/userinfo",
            action="fetch userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        email = user.get("email")
        return {
            "provider_account_id": str(user.get("sub")),
            "provider_username": email,
            "display_name": user.get("name") or email,
            "email": email,
            "profile_url": None,
            "avatar_url": user.get("picture"),
        }

    async def list_recent_messages(self, access_token: str, since: datetime) -> List[MailMessage]:
        headers = {"Authorization": f"Bearer {access_token}"}
        after = int(since.timestamp())
        # Gmail search: primary/updates categories carry recruiting mail.
        query = f"after:{after} -in:spam -in:trash"

        ids: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        while len(ids) < MAX_MESSAGES:
            url = (
                "https://gmail.googleapis.com/gmail/v1/users/me/messages"
                f"?q={urllib.parse.quote(query)}&maxResults=100"
            )
            if page_token:
                url += f"&pageToken={urllib.parse.quote(page_token)}"
            payload = await http.request_json(
                "Gmail", "GET", url, action="list messages", headers=headers
            )
            batch = payload.get("messages") or []
            ids.extend(batch)
            page_token = payload.get("nextPageToken")
            if not page_token or not batch:
                break

        messages: List[MailMessage] = []
        for entry in ids[:MAX_MESSAGES]:
            message_id = entry.get("id")
            if not message_id:
                continue
            try:
                detail = await http.request_json(
                    "Gmail",
                    "GET",
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
                    "?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date",
                    action="fetch message metadata",
                    headers=headers,
                )
            except ProviderError as exc:
                logger.info("Skipping Gmail message %s: %s", message_id, exc.detail)
                continue
            parsed = self._to_message(detail)
            if parsed:
                messages.append(parsed)
        return messages

    @staticmethod
    def _to_message(detail: Dict[str, Any]) -> Optional[MailMessage]:
        payload = detail.get("payload") or {}
        headers = {
            str(h.get("name", "")).lower(): h.get("value", "")
            for h in (payload.get("headers") or [])
        }
        subject = headers.get("subject", "")
        sender_name, sender_email = parseaddr(headers.get("from", ""))

        received_at: Optional[datetime] = None
        internal = detail.get("internalDate")
        if internal and str(internal).isdigit():
            received_at = datetime.fromtimestamp(int(internal) / 1000, tz=timezone.utc)
        elif headers.get("date"):
            try:
                received_at = parsedate_to_datetime(headers["date"])
            except (TypeError, ValueError):
                received_at = None

        message_id = detail.get("id")
        if not message_id:
            return None
        return MailMessage(
            message_id=message_id,
            thread_id=detail.get("threadId"),
            subject=subject,
            sender_name=sender_name or None,
            sender_email=sender_email or None,
            snippet=detail.get("snippet") or "",
            received_at=received_at,
            label_ids=detail.get("labelIds") or [],
            web_link=f"https://mail.google.com/mail/u/0/#inbox/{message_id}",
        )

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe("https://openidconnect.googleapis.com/v1/userinfo", expected=(200, 401))
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "missing_configuration": self.missing_configuration(),
            **result,
        }


# --------------------------------------------------------------------------- #
# Outlook / Microsoft Graph
# --------------------------------------------------------------------------- #

MICROSOFT_SCOPES = ("openid", "email", "profile", "offline_access", "Mail.Read", "User.Read")

MICROSOFT_DESCRIPTOR = ProviderDescriptor(
    name="microsoft",
    display_name="Microsoft Outlook",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset(
        {
            Capability.IDENTITY,
            Capability.PROFILE,
            Capability.EMAIL_READ,
            Capability.ACTIVITY,
            Capability.TOKEN_REFRESH,
        }
    ),
    scopes=MICROSOFT_SCOPES,
    allowed_url_hosts=("outlook.office.com", "outlook.live.com", "outlook.com"),
    docs_url="https://learn.microsoft.com/en-us/graph/permissions-reference",
    limitation_note=(
        "Read-only Outlook access. We scan recent mail for job-application activity "
        "and never send, modify or delete anything. Microsoft does not expose a token "
        "revocation endpoint, so disconnecting deletes our stored tokens; you can also "
        "remove the app from your Microsoft account permissions page."
    ),
)


class MicrosoftProvider(EmailConnector):
    supports_pkce = True

    @property
    def descriptor(self) -> ProviderDescriptor:
        return MICROSOFT_DESCRIPTOR

    @property
    def mailbox_url(self) -> str:
        return "https://outlook.office.com/mail/"

    @property
    def _authority(self) -> str:
        return f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}/oauth2/v2.0"

    def is_configured(self) -> bool:
        return bool(settings.MICROSOFT_CLIENT_ID and settings.MICROSOFT_CLIENT_SECRET)

    def missing_configuration(self) -> List[str]:
        missing = []
        if not settings.MICROSOFT_CLIENT_ID:
            missing.append("MICROSOFT_CLIENT_ID")
        if not settings.MICROSOFT_CLIENT_SECRET:
            missing.append("MICROSOFT_CLIENT_SECRET")
        return missing

    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        params = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(MICROSOFT_SCOPES),
            "state": state,
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{self._authority}/authorize?" + urllib.parse.urlencode(params)

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "scope": " ".join(MICROSOFT_SCOPES),
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        payload = await http.request_json(
            "Microsoft",
            "POST",
            f"{self._authority}/token",
            action="token exchange",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Microsoft did not issue an access token. Try connecting again.",
                detail=f"Microsoft token response: {payload.get('error')} {payload.get('error_description')}",
                code="token_exchange_failed",
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token"),
            "expires_in": payload.get("expires_in"),
            "scope": payload.get("scope"),
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = await http.request_json(
            "Microsoft",
            "POST",
            f"{self._authority}/token",
            action="token refresh",
            data={
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "scope": " ".join(MICROSOFT_SCOPES),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Outlook authorization expired. Reconnect required.",
                detail=f"Microsoft refresh response: {payload.get('error_description')}",
                code="reauth_required",
                requires_reauth=True,
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token") or refresh_token,
            "expires_in": payload.get("expires_in"),
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        user = await http.request_json(
            "Microsoft",
            "GET",
            "https://graph.microsoft.com/v1.0/me",
            action="fetch profile",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        email = user.get("mail") or user.get("userPrincipalName")
        return {
            "provider_account_id": str(user.get("id")),
            "provider_username": email,
            "display_name": user.get("displayName") or email,
            "email": email,
            "profile_url": None,
            "avatar_url": None,
        }

    async def list_recent_messages(self, access_token: str, since: datetime) -> List[MailMessage]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Prefer": 'outlook.body-content-type="text"',
        }
        filter_expr = f"receivedDateTime ge {since.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        url = (
            "https://graph.microsoft.com/v1.0/me/messages"
            f"?$filter={urllib.parse.quote(filter_expr)}"
            "&$select=id,conversationId,subject,from,bodyPreview,receivedDateTime,webLink"
            "&$orderby=receivedDateTime desc&$top=100"
        )

        messages: List[MailMessage] = []
        while url and len(messages) < MAX_MESSAGES:
            payload = await http.request_json(
                "Outlook", "GET", url, action="list messages", headers=headers
            )
            for item in payload.get("value") or []:
                parsed = self._to_message(item)
                if parsed:
                    messages.append(parsed)
                if len(messages) >= MAX_MESSAGES:
                    break
            url = payload.get("@odata.nextLink")
        return messages

    @staticmethod
    def _to_message(item: Dict[str, Any]) -> Optional[MailMessage]:
        message_id = item.get("id")
        if not message_id:
            return None
        sender = ((item.get("from") or {}).get("emailAddress")) or {}
        received_at: Optional[datetime] = None
        raw_received = item.get("receivedDateTime")
        if raw_received:
            try:
                received_at = datetime.fromisoformat(str(raw_received).replace("Z", "+00:00"))
            except ValueError:
                received_at = None
        return MailMessage(
            message_id=message_id,
            thread_id=item.get("conversationId"),
            subject=item.get("subject") or "",
            sender_name=sender.get("name"),
            sender_email=sender.get("address"),
            snippet=item.get("bodyPreview") or "",
            received_at=received_at,
            web_link=item.get("webLink"),
        )

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe(
            f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}/v2.0/.well-known/openid-configuration"
        )
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "missing_configuration": self.missing_configuration(),
            **result,
        }
