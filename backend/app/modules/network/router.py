from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
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
    NetworkingAnalyticsOut,
)

router = APIRouter(prefix="/network", tags=["Module 11 — AI Career Networking & Recruiter Relationship Engine"])


@router.post(
    "/contacts",
    response_model=ProfessionalContactOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new professional contact or recruiter into network CRM",
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
    "/contacts",
    response_model=List[ProfessionalContactOut],
    summary="List candidate network CRM directory",
)
def list_contacts(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.list_contacts(current_user.id)


@router.post(
    "/ai/generate-outreach",
    response_model=OutreachMessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized recruiter outreach draft requiring explicit human review and approval",
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
    "/outreach",
    response_model=List[OutreachMessageOut],
    summary="List all pending and historical outreach message drafts",
)
def list_outreach_drafts(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.list_outreach_drafts(current_user.id)


@router.post(
    "/ai/analyze-conversation",
    response_model=ConversationAnalysisOut,
    summary="Analyze recruiter response text, classify intent, and generate suggested reply",
)
def analyze_conversation(
    payload: ConversationAnalyzeQuery,
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.analyze_conversation(payload.message_text)


@router.get(
    "/analytics",
    response_model=NetworkingAnalyticsOut,
    summary="Get professional network CRM analytics and recruiter response metrics",
)
def get_networking_analytics(
    current_user: User = Depends(get_current_active_user),
    service: NetworkService = Depends(get_network_service),
):
    return service.get_networking_analytics(current_user.id)
