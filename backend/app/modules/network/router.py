from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.network.dependencies import get_network_service
from app.modules.network.service import NetworkService
from app.modules.network.schemas import (
    ProfessionalContactCreate,
    ProfessionalContactOut,
    OutreachGenerateQuery,
    OutreachMessageOut,
    ConversationAnalyzeQuery,
    ConversationAnalysisOut,
    ReferralOpportunityOut,
    PersonalBrandProfileOut,
    NetworkingAnalyticsOut,
)

router = APIRouter(prefix="", tags=["Module 16 — AI Career Network, Personal Brand & Referral Intelligence Engine"])


@router.post(
    "/network/contacts",
    response_model=ProfessionalContactOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new professional contact into network CRM",
)
def create_contact(
    payload: ProfessionalContactCreate,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.create_contact(
        user_id=current_user.id,
        name=payload.name,
        role=payload.role,
        company=payload.company,
        email=payload.email,
        profile_url=payload.profile_url,
        source=payload.source,
    )


@router.get(
    "/network/contacts",
    response_model=List[ProfessionalContactOut],
    summary="List candidate network CRM directory",
)
def list_contacts(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.list_contacts(current_user.id)


@router.post(
    "/network/ai/generate-outreach",
    response_model=OutreachMessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized outreach draft grounded in verified evidence requiring human approval",
)
def generate_outreach_draft(
    payload: OutreachGenerateQuery,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
    db: Session = Depends(get_db),
):
    return service.generate_outreach_draft(
        db=db,
        user_id=current_user.id,
        contact_id=payload.contact_id,
        purpose=payload.purpose,
        opportunity_title=payload.opportunity_title,
    )


@router.get(
    "/network/outreach",
    response_model=List[OutreachMessageOut],
    summary="List pending and historical outreach message drafts",
)
def list_outreach_drafts(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.list_outreach_drafts(current_user.id)


@router.post(
    "/network/outreach/{message_id}/approve",
    response_model=OutreachMessageOut,
    summary="Approve outreach message draft for submission (Human-in-the-Loop Gateway)",
)
def approve_outreach(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    res = service.approve_outreach(current_user.id, message_id)
    if not res:
        raise HTTPException(status_code=404, detail="Outreach message record not found")
    return res


@router.post(
    "/network/outreach/{message_id}/reject",
    response_model=OutreachMessageOut,
    summary="Reject outreach message draft",
)
def reject_outreach(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    res = service.reject_outreach(current_user.id, message_id)
    if not res:
        raise HTTPException(status_code=404, detail="Outreach message record not found")
    return res


@router.get(
    "/network/referrals",
    response_model=List[ReferralOpportunityOut],
    summary="List detected referral opportunities for target jobs",
)
def list_referrals(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.list_referrals(current_user.id)


@router.post(
    "/network/referrals/{referral_id}/approve",
    response_model=ReferralOpportunityOut,
    summary="Approve referral request outreach",
)
def approve_referral(
    referral_id: int,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    ref = service.approve_referral(current_user.id, referral_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Referral record not found")
    return ref


@router.get(
    "/brand/analysis",
    response_model=PersonalBrandProfileOut,
    summary="Get Personal Brand Score (0–100) and profile optimization recommendations",
)
def get_personal_brand(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.get_personal_brand(current_user.id)


@router.get(
    "/network/analytics",
    response_model=NetworkingAnalyticsOut,
    summary="Get professional network analytics and referral conversion metrics",
)
def get_networking_analytics(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.get_networking_analytics(current_user.id)
