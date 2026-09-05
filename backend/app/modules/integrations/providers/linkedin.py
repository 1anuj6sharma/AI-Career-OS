import httpx
from typing import Dict, Any, Optional
import urllib.parse

from app.core.config import settings
from .base import OAuthProvider, ProviderError

class LinkedInProvider(OAuthProvider):
    @property
    def provider_name(self) -> str:
        return "linkedin"

    def get_authorization_url(self, state: str) -> str:
        client_id = settings.LINKEDIN_CLIENT_ID
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/linkedin/callback"
        
        # OpenID Connect scopes (recommended for new LinkedIn apps)
        scope = "openid profile email"
        
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": scope
        }
        url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)
        return url

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"LinkedIn token exchange failed: {response.text}")
            
            token_data = response.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in")
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Failed to fetch LinkedIn profile: {response.text}")
            
            user_data = response.json()
            return {
                "provider_account_id": user_data.get("sub"),
                "provider_username": user_data.get("email"),  # LinkedIn doesn't always expose a vanity username here
                "display_name": user_data.get("name"),
                "profile_url": None, # Cannot easily get public profile URL from userinfo without r_basicprofile
                "avatar_url": user_data.get("picture")
            }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        # Without specific partner program approvals, LinkedIn APIs are very restricted.
        # We can only reliably get what's in the userinfo endpoint if we only have basic scopes.
        profile = await self.get_user_profile(access_token)
        return {
            "email": profile.get("provider_username"),
            "display_name": profile.get("display_name"),
            "status": "connected_basic"
        }
