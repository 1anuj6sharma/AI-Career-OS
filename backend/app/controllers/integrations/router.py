from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.database.session import get_db
from app.controllers.auth.dependencies import get_current_active_user
from app.models.auth import User
from app.views.integrations import (
    IntegrationLinkIn,
    IntegrationItemOut,
    IntegrationsStatusSummaryOut
)
from app.controllers.integrations.service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["Platform & Tool Integrations"])
integration_service = IntegrationService()

# In-memory simple state store for OAuth (In production use Redis)
oauth_states: Dict[str, int] = {}


@router.get(
    "/status",
    response_model=IntegrationsStatusSummaryOut,
    summary="Get all connected developer accounts and live telemetry status"
)
def get_integrations_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return integration_service.get_user_integrations_summary(db, current_user.id)


@router.get(
    "/{provider}/connect",
    summary="Initiate OAuth connection for an external developer platform"
)
async def connect_integration(
    provider: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Generate OAuth state to prevent CSRF
        state = str(uuid.uuid4())
        oauth_states[state] = current_user.id
        
        url = integration_service.get_authorization_url(provider.lower(), state)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{provider}/callback",
    summary="Handle OAuth callback"
)
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    frontend_redirect = f"{settings.FRONTEND_URL}/index.html" # Map to actual frontend URL logic

    if error:
        return RedirectResponse(f"{frontend_redirect}?error=oauth_denied&provider={provider}")

    if not code or not state:
        return RedirectResponse(f"{frontend_redirect}?error=invalid_request&provider={provider}")

    user_id = oauth_states.pop(state, None)
    if not user_id:
        return RedirectResponse(f"{frontend_redirect}?error=invalid_state&provider={provider}")

    try:
        redirect_uri = f"{settings.HOST}:{settings.PORT}/api/v1/integrations/{provider}/callback"
        await integration_service.handle_oauth_callback(
            db=db,
            user_id=user_id,
            provider_name=provider.lower(),
            code=code,
            redirect_uri=redirect_uri
        )
        return RedirectResponse(f"{frontend_redirect}?connected={provider}")
    except Exception as e:
        return RedirectResponse(f"{frontend_redirect}?error=connection_failed&provider={provider}&details={str(e)}")


@router.post(
    "/{provider}/link",
    response_model=IntegrationItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Link a public profile (LeetCode, GFG, Kaggle)"
)
async def link_integration(
    provider: str,
    payload: IntegrationLinkIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        integration = await integration_service.link_public_profile(
            db=db,
            user_id=current_user.id,
            provider_name=provider.lower(),
            identifier=payload.identifier
        )
        return integration
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/{provider}/sync",
    response_model=IntegrationItemOut,
    summary="Trigger on-demand data sync for a specific connected platform"
)
async def sync_platform_data(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    integration = await integration_service.sync_platform(db, current_user.id, provider.lower())
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {provider} is not currently connected."
        )
    return integration


@router.post(
    "/sync-all",
    response_model=List[IntegrationItemOut],
    summary="Trigger parallel synchronization across all connected developer platforms"
)
async def sync_all_integrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return await integration_service.sync_all_user_integrations(db, current_user.id)


@router.delete(
    "/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect an external platform"
)
def disconnect_platform(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    success = integration_service.disconnect_platform(db, current_user.id, provider.lower())
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {provider} is not connected."
        )
    return None
