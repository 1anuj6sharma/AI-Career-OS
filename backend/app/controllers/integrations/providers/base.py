from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProviderError(Exception):
    pass

class OAuthProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Return the URL to redirect the user to for authorization."""
        pass

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for tokens.
        Should return a dictionary containing 'access_token', 'refresh_token' (if applicable), and 'expires_in'.
        """
        pass

    @abstractmethod
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch the user's profile information using the access token.
        Should return a normalized dict: provider_account_id, provider_username, display_name, profile_url, avatar_url.
        """
        pass

    @abstractmethod
    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        """
        Fetch data for telemetry to be saved.
        """
        pass

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token using a refresh token.
        Raise NotImplementedError if the provider doesn't support refresh tokens or it's not implemented.
        """
        raise NotImplementedError("Token refresh not implemented for this provider.")

class PublicProfileProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        """
        Validate the public identifier (username or URL) and return normalized profile info:
        provider_account_id, provider_username, display_name, profile_url, avatar_url.
        Raise ProviderError if invalid or unreachable.
        """
        pass

    @abstractmethod
    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        """
        Fetch public telemetry data.
        """
        pass
