from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.opportunities.dependencies import get_opportunity_service
from app.modules.opportunities.service import OpportunityService
from app.modules.opportunities.schemas import (
    JobParseQuery,
    JobOpportunityOut,
)

router = APIRouter(prefix="/opportunities", tags=["Module 10 — AI Job Matching & Opportunity Intelligence Engine"])


@router.post(
    "/ai/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Parse job description, run multi-dimensional AI match, evaluate readiness, and generate application strategy",
)
def analyze_opportunity(
    payload: JobParseQuery,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
    db: Session = Depends(get_db),
):
    return service.analyze_and_create_opportunity(
        db=db,
        user_id=current_user.id,
        company_name=payload.company_name,
        title=payload.title,
        description=payload.description,
    )


@router.get(
    "/recommended",
    response_model=List[Dict[str, Any]],
    summary="List ranked job opportunities with match scores and readiness",
)
def list_recommended_opportunities(
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.list_recommended_opportunities(current_user.id)


@router.get(
    "/{job_id}",
    response_model=JobOpportunityOut,
    summary="Get detailed job opportunity intelligence and match details",
)
def get_opportunity(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.get_opportunity(job_id)
