"""
Connector registry — the single place a provider is added to the product.

`IntegrationManager` holds one instance per provider and is the only thing the
service and router talk to.  Adding a platform later means writing a connector
module and appending one line to `_CONNECTOR_CLASSES`.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Type

from .base import (
    AuthMethod,
    BaseConnector,
    Capability,
    ConnectionState,
    LinkOnlyProvider,
    OAuthProvider,
    ProviderAuthExpired,
    ProviderDescriptor,
    ProviderError,
    ProviderRateLimited,
    PublicProfileProvider,
    generate_pkce_verifier,
    pkce_challenge,
    sanitize_username,
    validate_external_url,
)
from .email_providers import EmailConnector, GoogleProvider, MicrosoftProvider
from .gfg import GFGProvider
from .github import GitHubProvider
from .huggingface import HuggingFaceProvider
from .kaggle import KaggleProvider
from .leetcode import LeetCodeProvider
from .linkedin import LinkedInProvider

#: Registration order is the display order in the UI.
_CONNECTOR_CLASSES: List[Type[BaseConnector]] = [
    GitHubProvider,
    LinkedInProvider,
    LeetCodeProvider,
    GFGProvider,
    GoogleProvider,
    MicrosoftProvider,
    KaggleProvider,
    HuggingFaceProvider,
]


class IntegrationManager:
    """Registry and lookup for provider connectors."""

    def __init__(self, connector_classes: Optional[Iterable[Type[BaseConnector]]] = None) -> None:
        self._connectors: Dict[str, BaseConnector] = {}
        for cls in connector_classes or _CONNECTOR_CLASSES:
            connector = cls()
            self._connectors[connector.provider_name] = connector

    # ------------------------------------------------------------------ lookup
    @property
    def provider_names(self) -> List[str]:
        return list(self._connectors.keys())

    def has(self, provider: str) -> bool:
        return bool(provider) and provider.lower() in self._connectors

    def get(self, provider: str) -> BaseConnector:
        connector = self._connectors.get((provider or "").lower())
        if connector is None:
            raise UnknownProviderError(provider)
        return connector

    def all(self) -> List[BaseConnector]:
        return list(self._connectors.values())

    def descriptors(self) -> List[ProviderDescriptor]:
        return [c.descriptor for c in self._connectors.values()]

    # ------------------------------------------------------------- capability
    def catalog(self) -> List[Dict[str, Any]]:
        """
        Provider metadata for the UI: what each platform supports, how it is
        connected, and any limitation to display.  Contains no user data and no
        secrets.
        """
        entries: List[Dict[str, Any]] = []
        for connector in self._connectors.values():
            desc = connector.descriptor
            configured = connector.is_configured()
            entries.append(
                {
                    "provider": desc.name,
                    "display_name": desc.display_name,
                    "auth_method": desc.auth_method.value,
                    "capabilities": sorted(c.value for c in desc.capabilities),
                    "scopes": list(desc.scopes),
                    "configured": configured,
                    "missing_configuration": connector.missing_configuration(),
                    "limitation_note": desc.limitation_note,
                    "docs_url": desc.docs_url,
                    "supports_sync": desc.auth_method is not AuthMethod.LINK_ONLY,
                    "supports_api_token": bool(getattr(connector, "supports_api_token", False)),
                    "api_token_label": getattr(connector, "api_token_label", None),
                    "api_token_help": getattr(connector, "api_token_help", None),
                    "default_state": self.default_state(desc.name).value,
                }
            )
        return entries

    def default_state(self, provider: str) -> ConnectionState:
        """The state an unconnected provider reports before any user action."""
        connector = self.get(provider)
        desc = connector.descriptor
        if desc.auth_method is AuthMethod.OAUTH2 and not connector.is_configured():
            return ConnectionState.CONFIGURATION_REQUIRED
        return ConnectionState.NOT_CONNECTED


class UnknownProviderError(ProviderError):
    def __init__(self, provider: str) -> None:
        super().__init__(
            "That platform is not supported.",
            detail=f"unknown provider requested: {provider!r}",
            code="unknown_provider",
        )


#: Process-wide manager. Connectors are stateless, so sharing them is safe.
integration_manager = IntegrationManager()


def get_provider(provider_name: str) -> BaseConnector:
    """Backwards-compatible accessor used by existing call sites."""
    return integration_manager.get(provider_name)


__all__ = [
    "AuthMethod",
    "BaseConnector",
    "Capability",
    "ConnectionState",
    "EmailConnector",
    "IntegrationManager",
    "LinkOnlyProvider",
    "OAuthProvider",
    "ProviderAuthExpired",
    "ProviderDescriptor",
    "ProviderError",
    "ProviderRateLimited",
    "PublicProfileProvider",
    "UnknownProviderError",
    "generate_pkce_verifier",
    "get_provider",
    "integration_manager",
    "pkce_challenge",
    "sanitize_username",
    "validate_external_url",
]
