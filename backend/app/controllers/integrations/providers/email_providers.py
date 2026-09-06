import httpx
from typing import Dict, Any
import urllib.parse

from app.core.config import settings
from .base import OAuthProvider, ProviderError

class GoogleProvider(OAuthProvider):
    @property
    def provider_name(self) -> str:
        return "google"

    def get_authorization_url(self, state: str) -> str:
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/google/callback"
        
        # Scopes for Gmail read access and profile
        scope = "openid email profile https://www.googleapis.com/auth/gmail.readonly"
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
        return url

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise ProviderError(f"Google token exchange failed: {response.text}")
            
            token_data = response.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in")
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Failed to fetch Google profile: {response.text}")
            
            user_data = response.json()
            return {
                "provider_account_id": user_data.get("id"),
                "provider_username": user_data.get("email"),
                "display_name": user_data.get("name"),
                "profile_url": None,
                "avatar_url": user_data.get("picture")
            }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        # Minimal implementation to get inbox info.
        url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return {
                    "email": identifier,
                    "status": "connected_basic"
                }
            
            data = response.json()
            return {
                "email": data.get("emailAddress"),
                "messages_total": data.get("messagesTotal"),
                "status": "connected_full"
            }


class MicrosoftProvider(OAuthProvider):
    @property
    def provider_name(self) -> str:
        return "microsoft"

    def get_authorization_url(self, state: str) -> str:
        client_id = settings.MICROSOFT_CLIENT_ID
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/microsoft/callback"
        
        scope = "openid email profile offline_access Mail.Read"
        
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": scope,
            "state": state
        }
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?" + urllib.parse.urlencode(params)
        return url

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "scope": "openid email profile offline_access Mail.Read",
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": settings.MICROSOFT_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, data=data, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Microsoft token exchange failed: {response.text}")
            
            token_data = response.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in")
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        url = "https://graph.microsoft.com/v1.0/me"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ProviderError(f"Failed to fetch Microsoft profile: {response.text}")
            
            user_data = response.json()
            return {
                "provider_account_id": user_data.get("id"),
                "provider_username": user_data.get("userPrincipalName"),
                "display_name": user_data.get("displayName"),
                "profile_url": None,
                "avatar_url": None
            }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        return {
            "email": identifier,
            "status": "connected_basic"
        }
