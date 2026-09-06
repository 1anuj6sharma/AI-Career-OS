"""
GeeksforGeeks connector — LINK ONLY.

GeeksforGeeks publishes no OAuth programme and no public API, and
https://www.geeksforgeeks.org/robots.txt disallows automated agents.  Scraping
the profile page would therefore be both unreliable and against the site's
stated wishes, and we will not ask a user for their GFG password (spec §11).

So this connector does exactly one honest thing: it records the profile URL the
user gives us, after verifying the URL shape belongs to geeksforgeeks.org, so
the [Open] button works and the account shows in the user's platform list.  It
reports LIMITED permanently and never claims a synchronization or reports a
single statistic.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import (
    AuthMethod,
    Capability,
    LinkOnlyProvider,
    ProviderDescriptor,
    ProviderError,
    sanitize_username,
)

LIMITATION = (
    "GeeksforGeeks does not offer an official API or OAuth, and its robots.txt "
    "disallows automated access. We store only your profile link so you can open it "
    "from here — practice statistics cannot be imported, and we will never ask for "
    "your GeeksforGeeks password."
)

DESCRIPTOR = ProviderDescriptor(
    name="gfg",
    display_name="GeeksforGeeks",
    auth_method=AuthMethod.LINK_ONLY,
    capabilities=frozenset({Capability.IDENTITY}),
    limitation_note=LIMITATION,
    docs_url="https://www.geeksforgeeks.org/",
    profile_url_template="https://www.geeksforgeeks.org/user/{username}/",
    allowed_url_hosts=("geeksforgeeks.org",),
)


class GFGProvider(LinkOnlyProvider):
    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        """
        Validate the handle/URL shape only.  We do not fetch the page, so we
        cannot and do not assert the profile exists — the status stays LIMITED
        and the UI says so.
        """
        username = sanitize_username(identifier)
        profile_url = DESCRIPTOR.profile_url_template.format(username=username)
        if not profile_url.startswith("https://www.geeksforgeeks.org/user/"):
            raise ProviderError("That does not look like a GeeksforGeeks profile.", code="invalid_identifier")
        return {
            "provider_account_id": username,
            "provider_username": username,
            "display_name": username,
            "email": None,
            "profile_url": profile_url,
            "avatar_url": None,
            "verified": False,
            "limitation_note": LIMITATION,
        }

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "configured": True,
            "reachable": None,
            "limitation_note": LIMITATION,
            "detail": "Link-only provider: no API is contacted.",
        }
