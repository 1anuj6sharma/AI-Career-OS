from typing import Dict, Any
import re

from .base import PublicProfileProvider, ProviderError

class KaggleProvider(PublicProfileProvider):
    @property
    def provider_name(self) -> str:
        return "kaggle"

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        username = identifier
        match = re.search(r'kaggle\.com/([^/]+)/?', identifier)
        if match:
            username = match.group(1)
            
        return {
            "provider_account_id": username,
            "provider_username": username,
            "display_name": username,
            "profile_url": f"https://www.kaggle.com/{username}",
            "avatar_url": None
        }

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        return {
            "username": identifier,
            "notebooks": 0,
            "models": 0,
            "medals": 0,
            "status": "linked_profile"
        }
