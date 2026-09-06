"""
Test doubles for the Connected Accounts module.

Every external platform call is replaced here.  Nothing in the test suite
performs a real HTTP request, and no test asserts against fabricated production
data — the fakes return small, explicit payloads that the assertions read back.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.controllers.integrations.providers.base import (
    AuthMethod,
    Capability,
    OAuthProvider,
    ProviderDescriptor,
    ProviderError,
    ProviderRateLimited,
    PublicProfileProvider,
)

FAKE_OAUTH_DESCRIPTOR = ProviderDescriptor(
    name="github",
    display_name="GitHub",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset(
        {
            Capability.IDENTITY,
            Capability.PROFILE,
            Capability.STATS,
            Capability.REPOSITORIES,
            Capability.TOKEN_REFRESH,
            Capability.TOKEN_REVOKE,
        }
    ),
    scopes=("read:user", "user:email"),
    profile_url_template="https://github.com/{username}",
    allowed_url_hosts=("github.com",),
)


class FakeOAuthProvider(OAuthProvider):
    """
    Stands in for GitHub.  Records what it was called with so tests can assert
    on the real flow (PKCE verifier forwarded, token refreshed before use,
    revocation attempted on disconnect) instead of trusting the service.
    """

    supports_pkce = True

    def __init__(self) -> None:
        self.exchange_calls: List[Dict[str, Any]] = []
        self.refresh_calls: List[str] = []
        self.revoke_calls: List[str] = []
        self.telemetry_calls: List[str] = []
        self.authorization_urls: List[str] = []

        #: Test knobs.
        self.configured = True
        self.exchange_error: Optional[ProviderError] = None
        self.profile_error: Optional[ProviderError] = None
        self.telemetry_error: Optional[ProviderError] = None
        #: Errors raised once each, in order, before succeeding — for retry tests.
        self.telemetry_transient_errors: List[ProviderError] = []
        self.profile_override: Optional[Dict[str, Any]] = None
        self.access_token = "gho_access_1"
        self.refreshed_access_token = "gho_access_2"
        self.refresh_response: Optional[Dict[str, Any]] = None
        self.expires_in: Optional[int] = None
        self.revoke_result = True

    @property
    def descriptor(self) -> ProviderDescriptor:
        return FAKE_OAUTH_DESCRIPTOR

    def is_configured(self) -> bool:
        return self.configured

    def missing_configuration(self) -> List[str]:
        return [] if self.configured else ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"]

    def get_authorization_url(
        self, state: str, redirect_uri: str, code_challenge: Optional[str] = None
    ) -> str:
        url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id=test&state={state}&redirect_uri={redirect_uri}"
            + (f"&code_challenge={code_challenge}&code_challenge_method=S256" if code_challenge else "")
        )
        self.authorization_urls.append(url)
        return url

    async def exchange_code(
        self, code: str, redirect_uri: str, code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        self.exchange_calls.append(
            {"code": code, "redirect_uri": redirect_uri, "code_verifier": code_verifier}
        )
        if self.exchange_error:
            raise self.exchange_error
        return {
            "access_token": self.access_token,
            "refresh_token": "ghr_refresh_1",
            "expires_in": self.expires_in,
            "scope": "read:user user:email",
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        if self.profile_error:
            raise self.profile_error
        if self.profile_override is not None:
            return self.profile_override
        return {
            "provider_account_id": "5551212",
            "provider_username": "octodev",
            "display_name": "Octo Dev",
            "email": "octo@example.com",
            "profile_url": "https://github.com/octodev",
            "avatar_url": "https://avatars.githubusercontent.com/u/5551212",
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        self.refresh_calls.append(refresh_token)
        if self.refresh_response is not None:
            if isinstance(self.refresh_response, ProviderError):
                raise self.refresh_response
            return self.refresh_response
        return {
            "access_token": self.refreshed_access_token,
            "refresh_token": "ghr_refresh_2",
            "expires_in": 3600,
        }

    async def revoke_token(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        self.revoke_calls.append(access_token)
        return self.revoke_result

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        self.telemetry_calls.append(access_token)
        if self.telemetry_transient_errors:
            raise self.telemetry_transient_errors.pop(0)
        if self.telemetry_error:
            raise self.telemetry_error
        return {
            "username": identifier,
            "repos_count": 7,
            "owned_repos_count": 5,
            "forks_count": 2,
            "total_stars": 13,
            "total_forks_received": 4,
            "recent_commits": 21,
            "top_languages": ["Python", "TypeScript"],
            "language_bytes": {"Python": 90000, "TypeScript": 21000},
            "organizations": [{"login": "acme", "url": "https://github.com/acme"}],
            "recent_repos": [
                {
                    "name": "career-os",
                    "full_name": f"{identifier}/career-os",
                    "url": f"https://github.com/{identifier}/career-os",
                    "description": "A real repository record",
                    "stars": 9,
                    "forks": 3,
                    "language": "Python",
                    "topics": ["fastapi"],
                    "pushed_at": "2026-08-30T10:00:00Z",
                }
            ],
            "activity_available": True,
        }

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "configured": self.configured,
            "missing_configuration": self.missing_configuration(),
            "reachable": True,
            "status_code": 200,
        }


FAKE_PUBLIC_DESCRIPTOR = ProviderDescriptor(
    name="leetcode",
    display_name="LeetCode",
    auth_method=AuthMethod.PUBLIC_USERNAME,
    capabilities=frozenset({Capability.IDENTITY, Capability.PROFILE, Capability.STATS}),
    limitation_note="LeetCode has no official public API; only public profile data is read.",
    profile_url_template="https://leetcode.com/u/{username}/",
    allowed_url_hosts=("leetcode.com",),
)


class FakePublicProvider(PublicProfileProvider):
    """Stands in for LeetCode: a public username, no credentials collected."""

    def __init__(self) -> None:
        self.profile_error: Optional[ProviderError] = None
        self.telemetry_error: Optional[ProviderError] = None
        self.telemetry_calls: List[str] = []

    @property
    def descriptor(self) -> ProviderDescriptor:
        return FAKE_PUBLIC_DESCRIPTOR

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        if self.profile_error:
            raise self.profile_error
        return {
            "provider_account_id": identifier,
            "provider_username": identifier,
            "display_name": identifier,
            "profile_url": f"https://leetcode.com/u/{identifier}/",
        }

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        self.telemetry_calls.append(identifier)
        if self.telemetry_error:
            raise self.telemetry_error
        return {
            "username": identifier,
            "solved_total": 12,
            "solved_easy": 7,
            "solved_medium": 4,
            "solved_hard": 1,
            "languages": [{"language": "Python3", "problemsSolved": 12}],
            "recent_solved": [
                {"slug": "two-sum", "title": "Two Sum", "timestamp": "1756500000"}
            ],
            "data_source": "leetcode public graphql",
        }


def rate_limited(retry_after: int = 1) -> ProviderRateLimited:
    return ProviderRateLimited(
        "LeetCode is rate limiting requests. Try again shortly.",
        retry_after=retry_after,
        detail="429 from provider",
    )
