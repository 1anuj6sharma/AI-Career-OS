import httpx
from typing import Dict, Any, Optional
import urllib.parse

from app.core.config import settings
from .base import OAuthProvider, ProviderError

class GitHubProvider(OAuthProvider):
    @property
    def provider_name(self) -> str:
        return "github"

    def get_authorization_url(self, state: str) -> str:
        client_id = settings.GITHUB_CLIENT_ID
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/github/callback"
        
        # We need repo scope if we want to see private repos, but public_repo or no scope is safer for public only
        # Let's request minimal scopes as requested. user:email for email.
        scope = "read:user user:email"
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state
        }
        url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)
        return url

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"GitHub token exchange failed: {response.text}")
            
            token_data = response.json()
            if "error" in token_data:
                raise ProviderError(f"GitHub token error: {token_data.get('error_description')}")
            
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),  # GH may not return this depending on app config
                "expires_in": token_data.get("expires_in")
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        url = "https://api.github.com/user"
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Career-OS"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Failed to fetch GitHub user: {response.text}")
            
            user_data = response.json()
            return {
                "provider_account_id": str(user_data.get("id")),
                "provider_username": user_data.get("login"),
                "display_name": user_data.get("name") or user_data.get("login"),
                "profile_url": user_data.get("html_url"),
                "avatar_url": user_data.get("avatar_url")
            }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Career-OS"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch repos
            res = await client.get(f"https://api.github.com/users/{identifier}/repos?per_page=100&sort=updated", headers=headers)
            if res.status_code != 200:
                raise ProviderError(f"Failed to fetch GitHub repos for {identifier}")
            
            repos = res.json()
            total_stars = sum(r.get("stargazers_count", 0) for r in repos)
            languages = list({r.get("language") for r in repos if r.get("language")})
            
            return {
                "username": identifier,
                "repos_count": len(repos),
                "total_stars": total_stars,
                "top_languages": languages[:10],
                "recent_repos": [
                    {"name": r["name"], "stars": r["stargazers_count"], "lang": r.get("language")}
                    for r in repos[:5]
                ]
            }
