"""
Hugging Face connector — OAuth 2.0 with PKCE.

Hugging Face implements OIDC ("Sign in with Hugging Face") at
https://huggingface.co/oauth/authorize with a documented `/oauth/userinfo`
endpoint, and its Hub API (https://huggingface.co/api) serves public model,
dataset and Space metadata.  Scope requested: `openid profile` only — reading
public repositories needs no scope at all.
"""
from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from app.core.config import settings

from . import http
from .base import (
    AuthMethod,
    Capability,
    OAuthProvider,
    ProviderDescriptor,
    ProviderError,
    sanitize_username,
)

HUB = "https://huggingface.co/api"
SCOPES = ("openid", "profile")

DESCRIPTOR = ProviderDescriptor(
    name="huggingface",
    display_name="Hugging Face",
    auth_method=AuthMethod.OAUTH2,
    capabilities=frozenset(
        {
            Capability.IDENTITY,
            Capability.PROFILE,
            Capability.STATS,
            Capability.ACTIVITY,
            Capability.REPOSITORIES,
        }
    ),
    scopes=SCOPES,
    profile_url_template="https://huggingface.co/{username}",
    allowed_url_hosts=("huggingface.co",),
    docs_url="https://huggingface.co/docs/hub/oauth",
)


class HuggingFaceProvider(OAuthProvider):
    supports_pkce = True

    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    def is_configured(self) -> bool:
        return bool(settings.HUGGINGFACE_CLIENT_ID and settings.HUGGINGFACE_CLIENT_SECRET)

    def missing_configuration(self) -> List[str]:
        missing = []
        if not settings.HUGGINGFACE_CLIENT_ID:
            missing.append("HUGGINGFACE_CLIENT_ID")
        if not settings.HUGGINGFACE_CLIENT_SECRET:
            missing.append("HUGGINGFACE_CLIENT_SECRET")
        return missing

    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
    ) -> str:
        params = {
            "client_id": settings.HUGGINGFACE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": " ".join(SCOPES),
            "state": state,
            "response_type": "code",
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return "https://huggingface.co/oauth/authorize?" + urllib.parse.urlencode(params)

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = {
            "client_id": settings.HUGGINGFACE_CLIENT_ID,
            "client_secret": settings.HUGGINGFACE_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        payload = await http.request_json(
            "Hugging Face", "POST", "https://huggingface.co/oauth/token", action="token exchange", data=data
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Hugging Face did not issue an access token. Try connecting again.",
                detail=f"HF token response: {payload}",
                code="token_exchange_failed",
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token"),
            "expires_in": payload.get("expires_in"),
            "scope": payload.get("scope"),
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = await http.request_json(
            "Hugging Face",
            "POST",
            "https://huggingface.co/oauth/token",
            action="token refresh",
            data={
                "client_id": settings.HUGGINGFACE_CLIENT_ID,
                "client_secret": settings.HUGGINGFACE_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if not payload.get("access_token"):
            raise ProviderError(
                "Hugging Face authorization expired. Reconnect required.",
                detail=f"HF refresh response: {payload}",
                code="reauth_required",
                requires_reauth=True,
            )
        return {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token") or refresh_token,
            "expires_in": payload.get("expires_in"),
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        user = await http.request_json(
            "Hugging Face",
            "GET",
            "https://huggingface.co/oauth/userinfo",
            action="fetch userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        username = user.get("preferred_username")
        return {
            "provider_account_id": str(user.get("sub")),
            "provider_username": username,
            "display_name": user.get("name") or username,
            "email": user.get("email"),
            "profile_url": user.get("profile") or (f"https://huggingface.co/{username}" if username else None),
            "avatar_url": user.get("picture"),
        }

    async def get_telemetry(self, access_token: str, identifier: str) -> Dict[str, Any]:
        """
        Public Hub metadata: models, datasets, Spaces, downloads and likes.
        The overview endpoint gives authoritative counts; the list endpoints
        give the individual artefacts used as portfolio evidence.
        """
        username = sanitize_username(identifier)
        headers = {"Authorization": f"Bearer {access_token}"}

        overview: Dict[str, Any] = {}
        try:
            overview = await http.request_json(
                "Hugging Face",
                "GET",
                f"{HUB}/users/{username}/overview",
                action="fetch overview",
                headers=headers,
            )
        except ProviderError:
            overview = {}

        models = await self._repos("models", username, headers)
        datasets = await self._repos("datasets", username, headers)
        spaces = await self._repos("spaces", username, headers)

        return {
            "username": username,
            "full_name": overview.get("fullname"),
            "is_pro": overview.get("isPro"),
            "followers": overview.get("numFollowers"),
            "upvotes_received": overview.get("numUpvotes"),
            "papers": overview.get("numPapers"),
            "organizations": [
                {"name": o.get("name"), "full_name": o.get("fullname")}
                for o in (overview.get("orgs") or [])
                if o.get("name")
            ][:20],
            "models_count": overview.get("numModels", len(models)),
            "datasets_count": overview.get("numDatasets", len(datasets)),
            "spaces_count": overview.get("numSpaces", len(spaces)),
            "total_model_downloads": sum(int(m.get("downloads") or 0) for m in models),
            "total_model_likes": sum(int(m.get("likes") or 0) for m in models),
            "models": [self._artefact("models", m) for m in models[:10]],
            "datasets": [self._artefact("datasets", d) for d in datasets[:10]],
            "spaces": [self._artefact("spaces", s) for s in spaces[:10]],
            "data_source": "Hugging Face Hub API",
        }

    async def _repos(self, kind: str, username: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        try:
            payload = await http.request_json(
                "Hugging Face",
                "GET",
                f"{HUB}/{kind}?author={username}&limit=100&sort=lastModified&direction=-1",
                action=f"list {kind}",
                headers=headers,
            )
        except ProviderError:
            return []
        return payload if isinstance(payload, list) else []

    @staticmethod
    def _artefact(kind: str, item: Dict[str, Any]) -> Dict[str, Any]:
        repo_id = item.get("id")
        prefix = {"models": "", "datasets": "datasets/", "spaces": "spaces/"}[kind]
        return {
            "id": repo_id,
            "url": f"https://huggingface.co/{prefix}{repo_id}" if repo_id else None,
            "likes": item.get("likes"),
            "downloads": item.get("downloads"),
            "tags": (item.get("tags") or [])[:12],
            "pipeline_tag": item.get("pipeline_tag"),
            "last_modified": item.get("lastModified"),
        }

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe(f"{HUB}/models?limit=1")
        return {
            "provider": self.provider_name,
            "configured": self.is_configured(),
            "missing_configuration": self.missing_configuration(),
            **result,
        }
