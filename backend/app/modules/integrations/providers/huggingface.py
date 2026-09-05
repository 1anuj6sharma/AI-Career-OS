import httpx
from typing import Dict, Any
import urllib.parse

from app.core.config import settings
from .base import OAuthProvider, ProviderError

class HuggingFaceProvider(OAuthProvider):
    @property
    def provider_name(self) -> str:
        return "huggingface"

    def get_authorization_url(self, state: str) -> str:
        client_id = settings.HUGGINGFACE_CLIENT_ID
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/huggingface/callback"
        
        scope = "read-repos"
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "response_type": "code"
        }
        url = "https://huggingface.co/oauth/authorize?" + urllib.parse.urlencode(params)
        return url

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = "https://huggingface.co/oauth/token"
        data = {
            "client_id": settings.HUGGINGFACE_CLIENT_ID,
            "client_secret": settings.HUGGINGFACE_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise ProviderError(f"HuggingFace token exchange failed: {response.text}")
            
            token_data = response.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in")
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        url = "https://huggingface.co/oauth/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Failed to fetch HuggingFace profile: {response.text}")
            
            user_data = response.json()
            return {
                "provider_account_id": user_data.get("sub"),
                "provider_username": user_data.get("preferred_username"),
                "display_name": user_data.get("name"),
                "profile_url": user_data.get("profile"),
                "avatar_url": user_data.get("picture")
            }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        profile = await self.get_user_profile(access_token)
        return {
            "username": profile.get("provider_username"),
            "status": "connected"
        }
