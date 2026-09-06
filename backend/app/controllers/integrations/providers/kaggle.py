"""
Kaggle connector — public API, with optional official API token.

Kaggle has no OAuth programme.  Its official public API (the one the `kaggle`
CLI speaks) is authenticated with a username + API token that the user
generates at https://www.kaggle.com/settings — that is an API credential, not a
password, and it is the mechanism Kaggle documents.  Providing it is optional.

Verified behaviour of https://www.kaggle.com/api/v1 at implementation time:
  * `datasets/list?user=<u>`  — works unauthenticated
  * `models/list?owner=<u>`   — works unauthenticated
  * `kernels/list?user=<u>`   — 401 Unauthenticated
  * `competitions/list`       — 401 Unauthenticated

So without a token we report datasets and models honestly and mark the account
LIMITED, explaining that notebooks and competition results need a token.  We
never fabricate medal or competition counts.
"""
from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

from . import http
from .base import (
    AuthMethod,
    Capability,
    ProviderDescriptor,
    ProviderError,
    PublicProfileProvider,
    sanitize_username,
)

API = "https://www.kaggle.com/api/v1"

LIMITATION_NO_TOKEN = (
    "Kaggle has no OAuth. Public datasets and models are imported without any credential. "
    "Notebooks, competition entries and medals require a Kaggle API token "
    "(kaggle.com → Settings → Create New Token), which you can add at any time."
)

DESCRIPTOR = ProviderDescriptor(
    name="kaggle",
    display_name="Kaggle",
    auth_method=AuthMethod.PUBLIC_USERNAME,
    capabilities=frozenset({Capability.IDENTITY, Capability.PROFILE, Capability.STATS}),
    limitation_note=LIMITATION_NO_TOKEN,
    docs_url="https://www.kaggle.com/docs/api",
    profile_url_template="https://www.kaggle.com/{username}",
    allowed_url_hosts=("kaggle.com",),
)


def _basic_auth(username: str, api_token: str) -> Dict[str, str]:
    encoded = base64.b64encode(f"{username}:{api_token}".encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


class KaggleProvider(PublicProfileProvider):
    #: This provider can optionally hold a user-supplied API token.
    supports_api_token = True
    api_token_label = "Kaggle API token"
    api_token_help = "Kaggle → Settings → API → Create New Token (the 'key' value in kaggle.json)"

    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        """
        Verify the username against a real Kaggle response.  A username with no
        public datasets is indistinguishable from a nonexistent one on the
        unauthenticated API, so we additionally confirm the profile page exists.
        """
        username = sanitize_username(identifier)
        exists = await http.probe(f"https://www.kaggle.com/{username}", expected=(200,))
        if exists.get("status_code") == 404:
            raise ProviderError(
                f"No public Kaggle profile found for '{username}'.",
                detail=f"Kaggle profile probe returned 404 for {username}",
                code="account_not_found",
            )
        if not exists.get("reachable"):
            raise ProviderError(
                "Could not reach Kaggle to verify that username. Try again shortly.",
                detail=f"Kaggle profile probe status={exists.get('status_code')}",
                code="provider_unavailable",
                retryable=True,
            )

        display_name = username
        datasets = await self._datasets(username)
        for item in datasets:
            owner = item.get("ownerNameNullable") or item.get("creatorNameNullable")
            if owner:
                display_name = owner
                break

        return {
            "provider_account_id": username,
            "provider_username": username,
            "display_name": display_name,
            "email": None,
            "profile_url": f"https://www.kaggle.com/{username}",
            "avatar_url": None,
        }

    async def get_telemetry(self, identifier: str, api_token: Optional[str] = None) -> Dict[str, Any]:
        username = sanitize_username(identifier)
        datasets = await self._datasets(username)
        models = await self._models(username)

        telemetry: Dict[str, Any] = {
            "username": username,
            "datasets_count": len(datasets),
            "total_dataset_downloads": sum(int(d.get("downloadCount") or 0) for d in datasets),
            "total_dataset_votes": sum(int(d.get("voteCount") or 0) for d in datasets),
            "datasets": [
                {
                    "title": d.get("titleNullable") or d.get("title"),
                    "url": d.get("urlNullable"),
                    "downloads": d.get("downloadCount"),
                    "votes": d.get("voteCount"),
                    "updated": d.get("lastUpdated"),
                }
                for d in datasets[:10]
            ],
            "models_count": len(models),
            "models": [
                {
                    "title": m.get("title"),
                    "url": f"https://www.kaggle.com/models/{m.get('ref')}" if m.get("ref") else None,
                    "downloads": m.get("downloadCount"),
                }
                for m in models[:10]
            ],
            # Explicitly null, not zero: we have not been able to look.
            "notebooks_count": None,
            "competitions_entered": None,
            "medals": None,
            "authenticated": False,
            "limitation_note": LIMITATION_NO_TOKEN,
            "data_source": "Kaggle public API v1 (unauthenticated)",
        }

        if api_token:
            telemetry.update(await self._authenticated_extras(username, api_token))
        return telemetry

    # ------------------------------------------------------------- public API
    async def _datasets(self, username: str) -> List[Dict[str, Any]]:
        collected: List[Dict[str, Any]] = []
        for page in range(1, 4):  # bounded pagination
            payload = await http.request_json(
                "Kaggle",
                "GET",
                f"{API}/datasets/list?user={username}&page={page}",
                action="list datasets",
            )
            if not isinstance(payload, list) or not payload:
                break
            collected.extend(payload)
            if len(payload) < 20:
                break
        return collected

    async def _models(self, username: str) -> List[Dict[str, Any]]:
        payload = await http.request_json(
            "Kaggle", "GET", f"{API}/models/list?owner={username}", action="list models"
        )
        if isinstance(payload, dict):
            models = payload.get("models")
            return models if isinstance(models, list) else []
        return payload if isinstance(payload, list) else []

    # ------------------------------------------------- authenticated API only
    async def _authenticated_extras(self, username: str, api_token: str) -> Dict[str, Any]:
        """
        With a user-supplied official token we can also read notebooks and the
        user's competition submissions.  Any failure here degrades to the
        unauthenticated picture instead of inventing numbers.
        """
        headers = _basic_auth(username, api_token)
        extras: Dict[str, Any] = {"authenticated": True, "data_source": "Kaggle public API v1 (token)"}

        try:
            kernels = await http.request_json(
                "Kaggle",
                "GET",
                f"{API}/kernels/list?user={username}&pageSize=100",
                action="list notebooks",
                headers=headers,
            )
        except ProviderError as exc:
            extras["authenticated"] = False
            extras["token_error"] = "Kaggle rejected the API token."
            extras["limitation_note"] = (
                "Kaggle rejected the stored API token, so notebooks and competition data "
                "were not imported. Re-add a token from kaggle.com → Settings."
            )
            extras["token_error_detail_logged"] = True
            _log_token_failure(exc)
            return extras

        kernel_list = kernels if isinstance(kernels, list) else []
        extras["notebooks_count"] = len(kernel_list)
        extras["notebooks"] = [
            {
                "title": k.get("title"),
                "url": f"https://www.kaggle.com/{k.get('ref')}" if k.get("ref") else None,
                "votes": k.get("totalVotes"),
                "language": k.get("language"),
            }
            for k in kernel_list[:10]
        ]

        try:
            comps = await http.request_json(
                "Kaggle",
                "GET",
                f"{API}/competitions/list?page=1",
                action="list competitions",
                headers=headers,
            )
            extras["competitions_visible"] = len(comps) if isinstance(comps, list) else 0
        except ProviderError:
            extras["competitions_visible"] = None

        # Kaggle's API exposes no per-user medal tally; stay honest about it.
        extras["medals"] = None
        extras["medals_note"] = "Kaggle's API does not expose a medal tally for a user."
        extras["limitation_note"] = (
            "Connected with your Kaggle API token. Datasets, models and notebooks are imported. "
            "Kaggle's API does not expose medal counts or per-user competition placements."
        )
        return extras

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe(f"{API}/datasets/list?page=1")
        return {
            "provider": self.provider_name,
            "configured": True,
            "limitation_note": LIMITATION_NO_TOKEN,
            **result,
        }


def _log_token_failure(exc: ProviderError) -> None:
    import logging

    logging.getLogger(__name__).warning("Kaggle token rejected: %s", exc.detail)
