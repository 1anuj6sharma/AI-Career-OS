from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.opportunities.dependencies import get_opportunity_service
from app.modules.opportunities.service import OpportunityService
from app.modules.opportunities.schemas import (
    JobParseQuery,
    JobOpportunityOut,
    OpportunityCreate,
    OpportunityScoreOut,
    ApplicationPrepareQuery,
    ApplicationApprovalPayload,
    ApplicationOut,
    ApplicationFeedbackOut,
    OpportunityAcquisitionDashboardOut,
)

router = APIRouter(tags=["Module 14 — AI Career Opportunity Intelligence & Job Acquisition Engine"])


# ----------------------------------------------------------------------------
# Module 10 Legacy Pipeline Compatibility
# ----------------------------------------------------------------------------
@router.post(
    "/opportunities/ai/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Parse job description, run multi-dimensional AI match, and generate application strategy",
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
    "/opportunities/recommended",
    response_model=List[Dict[str, Any]],
    summary="List ranked job opportunities with match scores",
)
def list_recommended_opportunities(
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.list_recommended_opportunities(current_user.id)


# ----------------------------------------------------------------------------
# Module 14 — Opportunity Acquisition & Discovery Endpoints
# ----------------------------------------------------------------------------
@router.get(
    "/opportunities",
    response_model=List[JobOpportunityOut],
    summary="List all discovered job opportunities",
)
def list_opportunities(
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.repo.list_opportunities()


@router.post(
    "/opportunities/discover",
    response_model=JobOpportunityOut,
    status_code=status.HTTP_201_CREATED,
    summary="Discover, normalize, and deduplicate job opportunity",
)
def discover_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.discover_opportunity(
        company_name=payload.company_name,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        remote_status=payload.remote_status,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        source=payload.source,
        external_job_id=payload.external_job_id,
    )


@router.get(
    "/opportunities/dashboard",
    response_model=OpportunityAcquisitionDashboardOut,
    summary="Get unified Opportunity Acquisition & Intelligence Dashboard",
)
def get_opportunity_dashboard(
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
    db: Session = Depends(get_db),
):
    return service.get_acquisition_dashboard(db, current_user.id)


@router.get(
    "/opportunities/{job_id}",
    response_model=JobOpportunityOut,
    summary="Get detailed job opportunity intelligence and match details",
)
def get_opportunity(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.get_opportunity(job_id)


@router.post(
    "/opportunities/{job_id}/evaluate",
    response_model=OpportunityScoreOut,
    summary="Evaluate opportunity and calculate deterministic Opportunity Score (0-100)",
)
def evaluate_opportunity(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
    db: Session = Depends(get_db),
):
    return service.evaluate_opportunity(db, current_user.id, job_id)


# ----------------------------------------------------------------------------
# Module 14 — Application Execution & Human Approval Gateway Endpoints
# ----------------------------------------------------------------------------
@router.post(
    "/applications/prepare",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Prepare application package (resume & cover letter) and pause at PENDING_APPROVAL",
)
def prepare_application(
    payload: ApplicationPrepareQuery,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
    db: Session = Depends(get_db),
):
    return service.prepare_application(db, current_user.id, payload.opportunity_id, payload.target_role)


@router.get(
    "/applications",
    response_model=List[ApplicationOut],
    summary="List candidate applications across stages",
)
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.list_applications(current_user.id, status_filter)


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationOut,
    summary="Get application package, documents, and event timeline",
)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    app = service.get_application(current_user.id, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post(
    "/applications/{application_id}/approve",
    response_model=ApplicationOut,
    summary="HUMAN APPROVAL GATEWAY — Approve prepared application for automated submission",
)
def approve_application(
    application_id: int,
    payload: Optional[ApplicationApprovalPayload] = None,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    notes = payload.notes if payload else None
    return service.approve_application(current_user.id, application_id, notes)


@router.post(
    "/applications/{application_id}/reject",
    response_model=ApplicationOut,
    summary="HUMAN APPROVAL GATEWAY — Reject prepared application",
)
def reject_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.reject_application(current_user.id, application_id)


@router.post(
    "/applications/{application_id}/submit",
    response_model=ApplicationOut,
    summary="Submit approved application via compliant API or handoff",
)
def submit_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.submit_application(current_user.id, application_id)


@router.get(
    "/career/opportunity-insights",
    response_model=ApplicationFeedbackOut,
    summary="Get closed-loop feedback learning insights across applications",
)
def get_opportunity_insights(
    current_user: User = Depends(get_current_active_user),
    service: OpportunityService = Depends(get_opportunity_service),
):
    return service.acq_service.analyze_feedback(current_user.id)
