from typing import Dict, Any
import re

from .base import PublicProfileProvider, ProviderError

class GeeksForGeeksProvider(PublicProfileProvider):
    @property
    def provider_name(self) -> str:
        return "gfg"

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        """
        GFG doesn't have a reliable open REST API, but we can do a basic validation of the handle/URL
        """
        handle = identifier
        match = re.search(r'geeksforgeeks\.org/user/([^/]+)/?', identifier)
        if match:
            handle = match.group(1)
            
        return {
            "provider_account_id": handle,
            "provider_username": handle,
            "display_name": handle,
            "profile_url": f"https://auth.geeksforgeeks.org/user/{handle}/",
            "avatar_url": None
        }

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        # Handle the case where the user entered an email as requested in the new UI
        handle = identifier.split('@')[0] if '@' in identifier else identifier
        match = re.search(r'geeksforgeeks\.org/user/([^/]+)/?', handle)
        if match:
            handle = match.group(1)

        url = f"https://auth.geeksforgeeks.org/user/{handle}/"
        import httpx
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                res = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                if res.status_code == 200:
                    html = res.text
                    
                    # Extract coding score (usually in the format "Coding Score.*?(\d+)")
                    score_match = re.search(r'Coding Score.*?(\d+)', html, re.IGNORECASE | re.DOTALL)
                    coding_score = int(score_match.group(1)) if score_match else 0
                    
                    # Extract total solved problems
                    solved_match = re.search(r'Problem Solved.*?(\d+)', html, re.IGNORECASE | re.DOTALL)
                    solved_problems = int(solved_match.group(1)) if solved_match else 0
                    
                    # Extract rank
                    rank_match = re.search(r'Institute Rank.*?<b>(\d+)</b>', html, re.IGNORECASE | re.DOTALL)
                    institute_rank = f"Top #{rank_match.group(1)} (Institute)" if rank_match else "N/A"
                    
                    # Also fallback for Next.js JSON payload if available
                    if coding_score == 0 and solved_problems == 0:
                        import json
                        next_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
                        if next_match:
                            try:
                                data = json.loads(next_match.group(1))
                                user_details = data.get('props', {}).get('pageProps', {}).get('userInfo', {})
                                coding_score = user_details.get('score', 0)
                                solved_problems = user_details.get('totalProblemsSolved', 0)
                                rank = user_details.get('instituteRank', '')
                                if rank:
                                    institute_rank = f"Top #{rank} (Institute)"
                            except:
                                pass
                    
                    return {
                        "handle": handle,
                        "coding_score": coding_score,
                        "solved_problems": solved_problems,
                        "institute_rank": institute_rank,
                        "status": "linked_profile"
                    }
            except Exception as e:
                pass
                
        # If parsing fails or times out, return zeroes
        return {
            "handle": handle,
            "coding_score": 0,
            "solved_problems": 0,
            "institute_rank": "N/A",
            "status": "linked_profile"
        }
