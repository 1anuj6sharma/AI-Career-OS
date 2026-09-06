"""
LinkedIn connector — OAuth 2.0 / OpenID Connect, deliberately LIMITED.

What LinkedIn's self-serve programme actually grants (products "Sign In with
LinkedIn using OpenID Connect" and "Share on LinkedIn"): the `openid profile
email` scopes and the `/v2/userinfo` endpoint.  That is identity only — name,
picture, email, and a stable `sub`.

Work history, connections, skills, endorsements and network data live behind
partner-only products that require LinkedIn's approval.  We therefore:
  * request nothing beyond identity scopes,
  * report the account as LIMITED with an explanation,
  * import no experience data, and
  * never scrape LinkedIn (spec §9).
"""
from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from app.core.config import settings

from . import http
from .base import (
    AuthMethod,
    Capability,
    OAuthProvider,
    ProviderDescriptor,
    ProviderError,
)

SCOPES = ("openid", "profile", "email")

LIMITATION = (
    "LinkedIn's self-serve API grants identity only (name, email, profile photo). "
    "Work history, skills and connections require LinkedIn partner approval, so they "
    "cannot be imported. We do not scrape LinkedIn."
)

DESCRIPTOR = ProviderDescriptor(
    name="linkedin",
    display_name="LinkedIn",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset({Capability.IDENTITY, Capability.PROFILE}),
    scopes=SCOPES,
    limitation_note=LIMITATION,
    docs_url="https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2",
    allowed_url_hosts=("linkedin.com",),
)


class LinkedInProvider(OAuthProvider):
    #: LinkedIn's token endpoint does not accept PKCE parameters.
    supports_pkce = False

    #: Read by the service to decide the persisted status: identity-only
    #: connections are CONNECTED for auth purposes but LIMITED for data.
    always_limited = True

    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    def is_configured(self) -> bool:
        return bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET)

    def missing_configuration(self) -> List[str]:
        missing = []
        if not settings.LINKEDIN_CLIENT_ID:
            missing.append("LINKEDIN_CLIENT_ID")
        if not settings.LINKEDIN_CLIENT_SECRET:
            missing.append("LINKEDIN_CLIENT_SECRET")
        return missing

    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(SCOPES),
        }
        return "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = await http.request_json(
            "LinkedIn",
            "POST",
            "https://www.linkedin.com/oauth/v2/accessToken",
            action="token exchange",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "LinkedIn did not issue an access token. Try connecting again.",
                detail=f"LinkedIn token response: {payload.get('error')} {payload.get('error_description')}",
                code="token_exchange_failed",
            )
        return {
            "access_token": payload["access_token"],
            # Refresh tokens are only issued to approved partner applications.
            "refresh_token": payload.get("refresh_token"),
            "expires_in": payload.get("expires_in"),
            "scope": payload.get("scope"),
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        user = await http.request_json(
            "LinkedIn",
            "GET",
            "https://api.linkedin.com/v2/userinfo",
            action="fetch userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        sub = user.get("sub")
        name = user.get("name") or " ".join(
            part for part in (user.get("given_name"), user.get("family_name")) if part
        )
        return {
            "provider_account_id": str(sub) if sub else None,
            # LinkedIn's OIDC response carries no vanity handle, so the display
            # name is the username surrogate — never the email address.
            "provider_username": name or None,
            "display_name": name or None,
            "email": user.get("email"),
            # The OIDC payload has no public profile URL; /in/me resolves to the
            # signed-in user's own profile in the browser.
            "profile_url": "https://www.linkedin.com/in/me/",
            "avatar_url": user.get("picture"),
            "email_verified": user.get("email_verified"),
        }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:  # noqa: ARG002
        """
        Identity confirmation only.  There is deliberately nothing else here:
        no counts, no experience, no connections — LinkedIn does not grant them.
        """
        profile = await self.get_user_profile(access_token)
        return {
            "username": profile.get("provider_username"),
            "email": profile.get("email"),
            "email_verified": profile.get("email_verified"),
            "identity_verified": True,
            "importable_data": ["name", "email", "profile photo"],
            "unavailable_data": [
                "work experience",
                "education",
                "skills and endorsements",
                "connections",
                "posts and activity",
            ],
            "limitation_note": LIMITATION,
            "data_source": "LinkedIn OpenID Connect /v2/userinfo",
        }

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe("https://www.linkedin.com/oauth/.well-known/openid-configuration")
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "missing_configuration": self.missing_configuration(),
            "limitation_note": LIMITATION,
            **result,
        }
