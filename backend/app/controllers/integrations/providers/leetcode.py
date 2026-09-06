import httpx
from typing import Dict, Any
import re

from .base import PublicProfileProvider, ProviderError

class LeetCodeProvider(PublicProfileProvider):
    @property
    def provider_name(self) -> str:
        return "leetcode"

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        """
        Identifier could be the username or the public URL: https://leetcode.com/u/<username>/
        """
        # Extract username if URL is provided
        username = identifier
        match = re.search(r'leetcode\.com(?:/u)?/([^/]+)/?', identifier)
        if match:
            username = match.group(1)
        
        # Test if valid using the unofficial stats API since LeetCode doesn't have an official REST API for this
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"https://leetcode-stats-api.herokuapp.com/{username}")
            if res.status_code != 200:
                raise ProviderError(f"Failed to validate LeetCode profile for {username}")
            
            data = res.json()
            if data.get("status") != "success":
                raise ProviderError(f"Invalid LeetCode username: {username}")
                
            return {
                "provider_account_id": username,
                "provider_username": username,
                "display_name": username,
                "profile_url": f"https://leetcode.com/u/{username}/",
                "avatar_url": None
            }

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        username = identifier
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"https://leetcode-stats-api.herokuapp.com/{username}")
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success":
                    return {
                        "username": username,
                        "total_solved": data.get("totalSolved", 0),
                        "easy_solved": data.get("easySolved", 0),
                        "medium_solved": data.get("mediumSolved", 0),
                        "hard_solved": data.get("hardSolved", 0),
                        "contest_rating": data.get("ranking", 0),
                        "percentile": data.get("reputation", 0) # API format varies, mapping roughly
                    }
        raise ProviderError(f"Failed to fetch LeetCode telemetry for {username}")
