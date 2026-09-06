"""
Connected Accounts & Tools API (spec §23).

    GET    /integrations                      overview for the current user
    GET    /integrations/catalog              static provider capabilities
    GET    /integrations/{provider}           one provider card
    GET    /integrations/{provider}/connect   start OAuth (returns authorize URL)
    GET    /integrations/{provider}/callback  OAuth redirect target
    POST   /integrations/{provider}/link      connect a non-OAuth platform
    POST   /integrations/{provider}/sync      real synchronization
    POST   /integrations/{provider}/disconnect  revoke + delete credentials
    DELETE /integrations/{provider}           alias of disconnect
    GET    /integrations/{provider}/health    reachability + token state

No response in this module contains an access token, a refresh token, an API
secret, a stack trace or a provider response body.
"""
from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.controllers.auth.dependencies import get_current_active_user
from app.controllers.integrations.service import (
    IntegrationServiceError,
    integration_service,
)
from app.core.config import settings
from app.core.logging import logger
from app.database.session import get_db
from app.models.auth import User
from app.views.integrations import (
    AuthorizationUrlOut,
    ConnectedAccountOut,
    DisconnectResultOut,
    HealthOut,
    IntegrationDisconnectIn,
    IntegrationLinkIn,
    IntegrationsOverviewOut,
    IntegrationSyncIn,
    ProviderCapabilityOut,
    SyncResultOut,
)

router = APIRouter(prefix="/integrations", tags=["Connected Accounts & Tools"])


def _http_error(exc: IntegrationServiceError) -> HTTPException:
    """Map a service error to an HTTP error carrying only user-safe text."""
    logger.info("Integration request failed [%s]: %s", exc.code, exc.detail)
    return HTTPException(
        status_code=exc.status_code,
        detail={"code": exc.code, "message": exc.message},
    )


def _frontend_redirect(params: Dict[str, str]) -> RedirectResponse:
    """
    Send the browser back to the app with a short, safe status code only.
    Never an exception message, never a provider body.
    """
    base = settings.FRONTEND_URL.rstrip("/")
    return RedirectResponse(f"{base}/?{urlencode(params)}#integrations")


# --------------------------------------------------------------------- reads

@router.get(
    "",
    response_model=IntegrationsOverviewOut,
    summary="All providers with the current user's real connection state",
)
def list_integrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return integration_service.list_accounts(db, current_user.id)


@router.get(
    "/status",
    response_model=IntegrationsOverviewOut,
    summary="Alias of GET /integrations (existing frontend contract)",
)
def integrations_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return integration_service.list_accounts(db, current_user.id)


@router.get(
    "/catalog",
    response_model=List[ProviderCapabilityOut],
    summary="Static provider capabilities and deployment configuration state",
)
def provider_catalog(_: User = Depends(get_current_active_user)):
    return integration_service.catalog()


# ------------------------------------------------------------------- OAuth

@router.get(
    "/{provider}/connect",
    response_model=AuthorizationUrlOut,
    summary="Start the OAuth flow for a provider",
)
def connect_integration(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        url = integration_service.begin_oauth(db, current_user.id, provider)
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc
    return {
        "provider": provider.lower(),
        "authorization_url": url,
        "url": url,
        "expires_in_seconds": settings.OAUTH_STATE_TTL_SECONDS,
    }


@router.get(
    "/{provider}/callback",
    include_in_schema=False,
    summary="OAuth redirect target",
)
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
):
    provider = provider.lower()
    params = request.query_params
    error = params.get("error")
    code = params.get("code")
    state = params.get("state")

    if error:
        # User denied consent, or the provider rejected the request.
        logger.info("OAuth denied for %s: %s", provider, error)
        reason = "oauth_denied" if error in {"access_denied", "user_cancelled_login"} else "oauth_error"
        return _frontend_redirect({"integration": provider, "error": reason})

    if not code:
        return _frontend_redirect({"integration": provider, "error": "missing_code"})

    try:
        user_id, verifier, redirect_uri = integration_service.consume_state(db, provider, state or "")
    except IntegrationServiceError as exc:
        logger.warning("OAuth state rejected for %s: %s", provider, exc.detail)
        return _frontend_redirect({"integration": provider, "error": exc.code})

    try:
        await integration_service.complete_oauth(
            db, user_id, provider, code=code, code_verifier=verifier, redirect_uri=redirect_uri
        )
    except IntegrationServiceError as exc:
        logger.warning("OAuth completion failed for %s: %s", provider, exc.detail)
        return _frontend_redirect({"integration": provider, "error": exc.code})

    return _frontend_redirect({"integration": provider, "connected": "1"})


# ------------------------------------------------------- non-OAuth linking

@router.post(
    "/{provider}/link",
    response_model=ConnectedAccountOut,
    status_code=status.HTTP_201_CREATED,
    summary="Connect a platform that has no OAuth (public profile or link-only)",
)
async def link_integration(
    provider: str,
    payload: IntegrationLinkIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        await integration_service.link_account(
            db,
            current_user.id,
            provider,
            identifier=payload.identifier,
            api_token=payload.api_token,
        )
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc
    return integration_service.get_account(db, current_user.id, provider)


# --------------------------------------------------------------------- sync

@router.post(
    "/{provider}/sync",
    response_model=SyncResultOut,
    summary="Run a real synchronization for one connected platform",
)
async def sync_integration(
    provider: str,
    payload: IntegrationSyncIn | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        return await integration_service.sync(
            db,
            current_user.id,
            provider,
            trigger="manual",
            force=bool(payload.force) if payload else False,
        )
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc


@router.post(
    "/sync-all",
    response_model=List[SyncResultOut],
    summary="Synchronize every connected, syncable platform",
)
async def sync_all_integrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return await integration_service.sync_all(db, current_user.id)


# --------------------------------------------------------------- disconnect

@router.post(
    "/{provider}/disconnect",
    response_model=DisconnectResultOut,
    summary="Revoke provider access and delete stored credentials",
)
async def disconnect_integration(
    provider: str,
    payload: IntegrationDisconnectIn | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        return await integration_service.disconnect(
            db,
            current_user.id,
            provider,
            purge_evidence=bool(payload.purge_evidence) if payload else False,
        )
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc


@router.delete(
    "/{provider}",
    response_model=DisconnectResultOut,
    summary="Alias of POST /{provider}/disconnect",
)
async def delete_integration(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        return await integration_service.disconnect(db, current_user.id, provider)
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc


# ------------------------------------------------------------------- health

@router.get(
    "/{provider}/health",
    response_model=HealthOut,
    summary="Provider reachability and local token state",
)
async def integration_health(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        return await integration_service.health(db, current_user.id, provider)
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc


@router.get(
    "/{provider}",
    response_model=ConnectedAccountOut,
    summary="One provider's real connection state for the current user",
)
def get_integration(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        return integration_service.get_account(db, current_user.id, provider)
    except IntegrationServiceError as exc:
        raise _http_error(exc) from exc
