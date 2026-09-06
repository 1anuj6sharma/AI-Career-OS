"""
Shared outbound HTTP helper for provider connectors.

Centralises timeouts, the User-Agent, rate-limit detection and the translation
of transport failures into `ProviderError`s carrying a user-safe message plus a
separate server-only detail (spec §24: never leak provider internals to a
browser).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

import httpx

from app.core.config import settings

from .base import ProviderAuthExpired, ProviderError, ProviderRateLimited

logger = logging.getLogger(__name__)

USER_AGENT = f"AI-Career-OS/{settings.APP_VERSION} (+integrations)"


def _timeout() -> httpx.Timeout:
    return httpx.Timeout(settings.PROVIDER_HTTP_TIMEOUT_SECONDS, connect=10.0)


def client(**kwargs: Any) -> httpx.AsyncClient:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    headers.update(kwargs.pop("headers", {}) or {})
    kwargs.setdefault("timeout", _timeout())
    kwargs.setdefault("follow_redirects", True)
    return httpx.AsyncClient(headers=headers, **kwargs)


def _retry_after(response: httpx.Response) -> Optional[int]:
    for header in ("Retry-After", "X-RateLimit-Reset"):
        raw = response.headers.get(header)
        if raw and raw.isdigit():
            return int(raw)
    return None


def raise_for_provider(
    provider: str,
    response: httpx.Response,
    *,
    action: str,
    expected: tuple = (200,),
) -> None:
    """
    Convert a non-success provider response into the right ProviderError
    subclass.  The response body goes to `detail` (logs) only.
    """
    if response.status_code in expected:
        return

    detail = f"{provider} {action} -> HTTP {response.status_code}: {response.text[:500]}"
    status = response.status_code

    if status in (401, 403):
        # GitHub uses 403 for both rate limits and permission problems.
        remaining = response.headers.get("X-RateLimit-Remaining")
        if status == 403 and remaining == "0":
            raise ProviderRateLimited(
                f"{provider} rate limit reached. Try again shortly.",
                retry_after=_retry_after(response),
                detail=detail,
            )
        if status == 401:
            raise ProviderAuthExpired(
                f"{provider} authorization is no longer valid. Reconnect required.",
                detail=detail,
            )
        raise ProviderError(
            f"{provider} refused the request. The connection may be missing a required permission.",
            detail=detail,
            code="insufficient_scope",
        )
    if status == 404:
        raise ProviderError(
            f"{provider} could not find that account.",
            detail=detail,
            code="account_not_found",
        )
    if status == 429:
        raise ProviderRateLimited(
            f"{provider} rate limit reached. Try again shortly.",
            retry_after=_retry_after(response),
            detail=detail,
        )
    if status >= 500:
        raise ProviderError(
            f"{provider} is currently unavailable. Try again later.",
            detail=detail,
            code="provider_unavailable",
            retryable=True,
        )
    raise ProviderError(
        f"{provider} rejected the request.",
        detail=detail,
        code="provider_error",
    )


async def request_json(
    provider: str,
    method: str,
    url: str,
    *,
    action: str,
    headers: Optional[Mapping[str, str]] = None,
    expected: tuple = (200,),
    **kwargs: Any,
) -> Any:
    """Perform a request and return parsed JSON, mapping every failure mode."""
    try:
        async with client() as http:
            response = await http.request(method, url, headers=dict(headers or {}), **kwargs)
    except httpx.TimeoutException as exc:
        raise ProviderError(
            f"{provider} did not respond in time. Try again.",
            detail=f"{provider} {action} timeout: {exc!r}",
            code="timeout",
            retryable=True,
        ) from exc
    except httpx.HTTPError as exc:
        raise ProviderError(
            f"Could not reach {provider}. Check your connection and try again.",
            detail=f"{provider} {action} transport error: {exc!r}",
            code="network_error",
            retryable=True,
        ) from exc

    raise_for_provider(provider, response, action=action, expected=expected)

    try:
        return response.json()
    except ValueError as exc:
        raise ProviderError(
            f"{provider} returned an unexpected response.",
            detail=f"{provider} {action} non-JSON body: {response.text[:300]}",
            code="invalid_response",
        ) from exc


async def probe(url: str, *, expected: tuple = (200,)) -> Dict[str, Any]:
    """Reachability probe for health_check; never raises."""
    try:
        async with client() as http:
            response = await http.get(url)
        return {"reachable": response.status_code in expected, "status_code": response.status_code}
    except httpx.HTTPError as exc:
        logger.info("Health probe failed for %s: %r", url, exc)
        return {"reachable": False, "status_code": None}
