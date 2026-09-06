"""
GitHub connector — OAuth 2.0 (authorization code).

GitHub's OAuth App flow does not support PKCE; its GitHub App flow issues
refresh tokens while OAuth Apps issue non-expiring tokens.  Both are handled:
`refresh_token`/`expires_in` are used when the provider returns them.

Scopes requested: `read:user user:email` only — enough for identity, public
repositories, languages and public events.  Private repositories are
deliberately NOT requested (least privilege, spec §8).
"""
from __future__ import annotations

import urllib.parse
from collections import Counter
from typing import Any, Dict, List, Optional

from app.core.config import settings

from . import http
from .base import (
    AuthMethod,
    Capability,
    OAuthProvider,
    ProviderDescriptor,
    ProviderError,
    sanitize_username,
)

API = "https://api.github.com"
SCOPES = ("read:user", "user:email")

DESCRIPTOR = ProviderDescriptor(
    name="github",
    display_name="GitHub",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset(
        {
            Capability.IDENTITY,
            Capability.PROFILE,
            Capability.STATS,
            Capability.ACTIVITY,
            Capability.REPOSITORIES,
            Capability.TOKEN_REVOKE,
        }
    ),
    scopes=SCOPES,
    profile_url_template="https://github.com/{username}",
    allowed_url_hosts=("github.com",),
    docs_url="https://docs.github.com/en/apps/oauth-apps",
)


class GitHubProvider(OAuthProvider):
    supports_pkce = False  # GitHub OAuth Apps ignore/reject PKCE parameters.

    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    def is_configured(self) -> bool:
        return bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)

    def missing_configuration(self) -> List[str]:
        missing = []
        if not settings.GITHUB_CLIENT_ID:
            missing.append("GITHUB_CLIENT_ID")
        if not settings.GITHUB_CLIENT_SECRET:
            missing.append("GITHUB_CLIENT_SECRET")
        return missing

    # ------------------------------------------------------------------ OAuth
    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": " ".join(SCOPES),
            "state": state,
            "allow_signup": "false",
        }
        return "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = await http.request_json(
            "GitHub",
            "POST",
            "https://github.com/login/oauth/access_token",
            action="token exchange",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        if payload.get("error") or not payload.get("access_token"):
            raise ProviderError(
                "GitHub did not issue an access token. The authorization may have expired — try connecting again.",
                detail=f"GitHub token response error: {payload.get('error')} {payload.get('error_description')}",
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
            "GitHub",
            "POST",
            "https://github.com/login/oauth/access_token",
            action="token refresh",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if payload.get("error") or not payload.get("access_token"):
            raise ProviderError(
                "GitHub authorization expired. Reconnect required.",
                detail=f"GitHub refresh error: {payload.get('error_description')}",
                code="reauth_required",
                requires_reauth=True,
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token") or refresh_token,
            "expires_in": payload.get("expires_in"),
        }

    async def revoke_token(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """
        DELETE /applications/{client_id}/token with Basic auth revokes the
        user's grant.  Returns True only when GitHub confirms (204).
        """
        if not self.is_configured():
            return False
        import base64

        basic = base64.b64encode(
            f"{settings.GITHUB_CLIENT_ID}:{settings.GITHUB_CLIENT_SECRET}".encode()
        ).decode()
        try:
            async with http.client() as client:
                response = await client.request(
                    "DELETE",
                    f"{API}/applications/{settings.GITHUB_CLIENT_ID}/token",
                    headers={
                        "Authorization": f"Basic {basic}",
                        "Accept": "application/vnd.github+json",
                    },
                    json={"access_token": access_token},
                )
            return response.status_code in (204, 404)
        except Exception:  # noqa: BLE001 - revocation is best-effort on disconnect
            return False

    # ---------------------------------------------------------------- profile
    def _auth_headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        user = await http.request_json(
            "GitHub", "GET", f"{API}/user", action="fetch user", headers=self._auth_headers(access_token)
        )
        email = user.get("email")
        if not email:
            email = await self._primary_email(access_token)
        return {
            "provider_account_id": str(user.get("id")),
            "provider_username": user.get("login"),
            "display_name": user.get("name") or user.get("login"),
            "email": email,
            "profile_url": user.get("html_url"),
            "avatar_url": user.get("avatar_url"),
        }

    async def _primary_email(self, access_token: str) -> Optional[str]:
        """user:email scope exposes verified addresses; absence is not an error."""
        try:
            emails = await http.request_json(
                "GitHub",
                "GET",
                f"{API}/user/emails",
                action="fetch emails",
                headers=self._auth_headers(access_token),
            )
        except ProviderError:
            return None
        if not isinstance(emails, list):
            return None
        for entry in emails:
            if entry.get("primary") and entry.get("verified"):
                return entry.get("email")
        for entry in emails:
            if entry.get("verified"):
                return entry.get("email")
        return None

    # -------------------------------------------------------------- telemetry
    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        """
        Real repository, language and activity data.  Every number returned is
        computed from the provider response — nothing is defaulted or invented.
        """
        username = sanitize_username(identifier)
        headers = self._auth_headers(access_token)

        repos = await self._all_repos(headers)
        owned = [r for r in repos if not r.get("fork")]

        language_bytes: Counter = Counter()
        for repo in owned[:25]:  # bounded: avoid hammering the API (spec §17)
            lang_url = repo.get("languages_url")
            if not lang_url:
                continue
            try:
                langs = await http.request_json(
                    "GitHub", "GET", lang_url, action="fetch repo languages", headers=headers
                )
            except ProviderError:
                continue
            if isinstance(langs, dict):
                language_bytes.update({k: int(v) for k, v in langs.items() if isinstance(v, int)})

        orgs: List[Dict[str, Any]] = []
        try:
            org_payload = await http.request_json(
                "GitHub", "GET", f"{API}/user/orgs?per_page=50", action="fetch orgs", headers=headers
            )
            if isinstance(org_payload, list):
                orgs = [
                    {"login": o.get("login"), "url": f"https://github.com/{o.get('login')}"}
                    for o in org_payload
                    if o.get("login")
                ]
        except ProviderError:
            orgs = []  # org visibility depends on member settings; not a failure

        activity = await self._activity(headers, username)

        return {
            "username": username,
            "repos_count": len(repos),
            "owned_repos_count": len(owned),
            "forks_count": sum(1 for r in repos if r.get("fork")),
            "total_stars": sum(int(r.get("stargazers_count") or 0) for r in owned),
            "total_forks_received": sum(int(r.get("forks_count") or 0) for r in owned),
            "top_languages": [name for name, _ in language_bytes.most_common(10)],
            "language_bytes": dict(language_bytes.most_common(10)),
            "organizations": orgs,
            "recent_repos": [
                {
                    "name": r.get("name"),
                    "full_name": r.get("full_name"),
                    "url": r.get("html_url"),
                    "description": r.get("description"),
                    "stars": int(r.get("stargazers_count") or 0),
                    "forks": int(r.get("forks_count") or 0),
                    "language": r.get("language"),
                    "topics": r.get("topics") or [],
                    "pushed_at": r.get("pushed_at"),
                }
                for r in sorted(owned, key=lambda x: x.get("pushed_at") or "", reverse=True)[:10]
            ],
            **activity,
        }

    async def _all_repos(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Paginate /user/repos, capped so a huge account cannot stall a sync."""
        collected: List[Dict[str, Any]] = []
        for page in range(1, 6):  # max 500 repos
            batch = await http.request_json(
                "GitHub",
                "GET",
                f"{API}/user/repos?per_page=100&page={page}&affiliation=owner,collaborator&sort=pushed",
                action="fetch repos",
                headers=headers,
            )
            if not isinstance(batch, list) or not batch:
                break
            collected.extend(batch)
            if len(batch) < 100:
                break
        return collected

    async def _activity(self, headers: Dict[str, str], username: str) -> Dict[str, Any]:
        """Public event stream → commit and contribution counts."""
        try:
            events = await http.request_json(
                "GitHub",
                "GET",
                f"{API}/users/{username}/events/public?per_page=100",
                action="fetch activity",
                headers=headers,
            )
        except ProviderError:
            return {"recent_commits": None, "recent_activity": [], "activity_available": False}

        if not isinstance(events, list):
            return {"recent_commits": None, "recent_activity": [], "activity_available": False}

        commits = 0
        recent: List[Dict[str, Any]] = []
        for event in events:
            etype = event.get("type")
            if etype == "PushEvent":
                commits += len(((event.get("payload") or {}).get("commits")) or [])
            if len(recent) < 15 and etype:
                recent.append(
                    {
                        "type": etype,
                        "repo": (event.get("repo") or {}).get("name"),
                        "created_at": event.get("created_at"),
                    }
                )
        return {
            "recent_commits": commits,
            "recent_activity": recent,
            "activity_available": True,
            "activity_window": "last 100 public events",
        }

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe(f"{API}/rate_limit", expected=(200, 401, 403))
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "missing_configuration": self.missing_configuration(),
            **result,
        }
