"""
Provider connector contract for the Connected Accounts & Tools module.

Every external platform is represented by a connector class that declares, up
front, what it can honestly do (`capabilities`) and how a user authenticates
(`auth_method`).  Callers never guess: they read the declaration and drive the
correct flow.  A connector that cannot legitimately reach a provider must say so
via `ConnectionState.NOT_SUPPORTED` / `LIMITED` rather than returning fabricated
data.
"""
from __future__ import annotations

import base64
import hashlib
import re
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class ProviderError(Exception):
    """
    Raised by connectors for any provider-side failure.

    `user_message` is safe to show a user.  `detail` is for server logs only and
    must never be sent to a browser (spec §24).
    """

    def __init__(
        self,
        user_message: str,
        *,
        detail: Optional[str] = None,
        code: str = "provider_error",
        retryable: bool = False,
        requires_reauth: bool = False,
    ) -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.detail = detail or user_message
        self.code = code
        self.retryable = retryable
        self.requires_reauth = requires_reauth


class ProviderRateLimited(ProviderError):
    def __init__(self, user_message: str, *, retry_after: Optional[int] = None, detail: Optional[str] = None):
        super().__init__(user_message, detail=detail, code="rate_limited", retryable=True)
        self.retry_after = retry_after


class ProviderAuthExpired(ProviderError):
    def __init__(self, user_message: str, *, detail: Optional[str] = None):
        super().__init__(user_message, detail=detail, code="reauth_required", requires_reauth=True)


class ConnectionState(str, Enum):
    """The only connection states the product is allowed to report."""

    NOT_CONNECTED = "NOT_CONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    SYNCING = "SYNCING"
    SYNCED = "SYNCED"
    SYNC_FAILED = "SYNC_FAILED"
    REAUTH_REQUIRED = "REAUTH_REQUIRED"
    LIMITED = "LIMITED"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class AuthMethod(str, Enum):
    OAUTH2 = "OAUTH2"              # full OAuth 2.0 authorization-code flow
    PUBLIC_USERNAME = "PUBLIC_USERNAME"  # public, documented read-only endpoint
    API_KEY = "API_KEY"            # user-supplied API token for their own account
    LINK_ONLY = "LINK_ONLY"        # no programmatic access: we store a profile link only


class Capability(str, Enum):
    IDENTITY = "IDENTITY"
    PROFILE = "PROFILE"
    STATS = "STATS"
    ACTIVITY = "ACTIVITY"
    REPOSITORIES = "REPOSITORIES"
    EMAIL_READ = "EMAIL_READ"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    TOKEN_REVOKE = "TOKEN_REVOKE"


@dataclass(frozen=True)
class ProviderDescriptor:
    """Static, honest description of what a connector supports."""

    name: str
    display_name: str
    auth_method: AuthMethod
    capabilities: frozenset = field(default_factory=frozenset)
    # Human-readable explanation shown in the UI when the provider is LIMITED,
    # NOT_SUPPORTED or CONFIGURATION_REQUIRED.
    limitation_note: Optional[str] = None
    # Docs URL the user can read to understand the limitation.
    docs_url: Optional[str] = None
    # OAuth scopes actually requested (least privilege, spec §5/§27).
    scopes: tuple = ()
    # Where the user's public profile lives, for the [Open] button.
    profile_url_template: Optional[str] = None
    # Provider host allow-list used to validate any URL we hand the browser.
    allowed_url_hosts: tuple = ()

    def supports(self, capability: Capability) -> bool:
        return capability in self.capabilities


# --------------------------------------------------------------------------- #
# PKCE helpers (spec §5)
# --------------------------------------------------------------------------- #

def generate_pkce_verifier() -> str:
    """RFC 7636 code_verifier: 43-128 chars of unreserved characters."""
    return base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("ascii").rstrip("=")


def pkce_challenge(verifier: str) -> str:
    """S256 code_challenge for a verifier."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,62}[A-Za-z0-9])?$")


def sanitize_username(raw: str) -> str:
    """
    Accept a bare username or a profile URL and return the bare username.

    Raises ProviderError on anything that is not a plausible handle, so a
    malformed value can never be interpolated into an outbound request.
    """
    if not raw or not raw.strip():
        raise ProviderError("A username is required.", code="invalid_identifier")
    value = raw.strip()
    if "://" in value or value.startswith("www."):
        parsed = urlparse(value if "://" in value else f"https://{value}")
        segments = [seg for seg in (parsed.path or "").split("/") if seg]
        if not segments:
            raise ProviderError("That profile link does not contain a username.", code="invalid_identifier")
        value = segments[-1]
    value = value.lstrip("@").rstrip("/")
    if not _USERNAME_RE.match(value):
        raise ProviderError(
            "That username contains characters we cannot accept.",
            code="invalid_identifier",
            detail=f"rejected identifier of length {len(value)}",
        )
    return value


def validate_external_url(url: Optional[str], allowed_hosts: tuple) -> Optional[str]:
    """
    Return `url` only if it is https and its host is in `allowed_hosts`
    (spec §19: safe external URL validation).  Otherwise return None.
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    for allowed in allowed_hosts:
        allowed = allowed.lower()
        if host == allowed or host.endswith(f".{allowed}"):
            return url
    return None


# --------------------------------------------------------------------------- #
# Connector base classes
# --------------------------------------------------------------------------- #

class BaseConnector(ABC):
    """Common surface shared by every connector, whatever its auth method."""

    @property
    @abstractmethod
    def descriptor(self) -> ProviderDescriptor:
        ...

    @property
    def provider_name(self) -> str:
        return self.descriptor.name

    def is_configured(self) -> bool:
        """
        False when required deployment configuration (client id/secret) is
        absent, which surfaces as CONFIGURATION_REQUIRED instead of a
        confusing runtime failure.
        """
        return True

    def missing_configuration(self) -> List[str]:
        """Names of the environment variables that still need to be set."""
        return []

    def get_external_url(self, account: Dict[str, Any]) -> Optional[str]:
        """
        Build the [Open] target for a connected account.  Prefers a URL the
        provider itself gave us; falls back to the template.  Always validated
        against the provider's host allow-list.
        """
        desc = self.descriptor
        stored = validate_external_url(account.get("profile_url"), desc.allowed_url_hosts)
        if stored:
            return stored
        username = account.get("provider_username")
        if desc.profile_url_template and username:
            try:
                candidate = desc.profile_url_template.format(username=sanitize_username(username))
            except ProviderError:
                return None
            return validate_external_url(candidate, desc.allowed_url_hosts)
        return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Cheap reachability probe that never touches user tokens.  Connectors
        override with a real request where one exists.
        """
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "reachable": None,
            "detail": "No health probe implemented for this provider.",
        }


class OAuthProvider(BaseConnector):
    """OAuth 2.0 authorization-code connector (with PKCE where supported)."""

    #: Set False for providers whose token endpoint rejects PKCE parameters.
    supports_pkce: bool = True

    @abstractmethod
    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        ...

    @abstractmethod
    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return {'access_token', 'refresh_token'?, 'expires_in'?, 'scope'?}."""
        ...

    @abstractmethod
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Normalized identity: provider_account_id, provider_username,
        display_name, email, profile_url, avatar_url.
        """
        ...

    @abstractmethod
    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        ...

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.provider_name} does not support token refresh.")

    async def revoke_token(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """
        Revoke the token provider-side on disconnect.  Return True when the
        provider confirmed revocation, False when it offers no revoke endpoint.
        """
        return False


class PublicProfileProvider(BaseConnector):
    """
    Connector for platforms that expose a documented, public, read-only
    endpoint for data the user has already made public.  No credentials are
    ever collected from the user.
    """

    @abstractmethod
    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        ...


class LinkOnlyProvider(BaseConnector):
    """
    Connector for platforms with no legitimate programmatic access.  It stores
    a verified profile link so the [Open] button works and the account appears
    in the user's evidence trail, and it reports LIMITED forever.  It never
    claims a sync.
    """

    @abstractmethod
    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        ...

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:  # noqa: ARG002
        raise ProviderError(
            self.descriptor.limitation_note or "This platform cannot be synchronized.",
            code="not_supported",
        )
