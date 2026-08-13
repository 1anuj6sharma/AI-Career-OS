from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.career.dependencies import get_career_service
from app.modules.career.service import CareerService
from app.modules.career.schemas import (
    CareerRoadmapOut,
    CareerProgressMetricsOut,
    CareerCoachQuery,
    CareerCoachResponse,
)

router = APIRouter(prefix="/career", tags=["Module 7 — AI Career Execution & Adaptive Growth Engine"])


@router.post(
    "/roadmaps/generate",
    response_model=CareerRoadmapOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new versioned career roadmap with milestones and Module 3 task scheduling",
)
def generate_roadmap(
    target_role: Optional[str] = Query(None, description="Target career role (e.g. Senior Backend Engineer)"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.generate_roadmap(db, current_user.id, target_role)


@router.get(
    "/roadmaps/active",
    response_model=CareerRoadmapOut,
    summary="Get currently active career roadmap version",
)
def get_active_roadmap(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.get_active_roadmap(current_user.id)


@router.get(
    "/roadmaps",
    response_model=List[CareerRoadmapOut],
    summary="List all historical and adapted career roadmap versions",
)
def list_roadmaps(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_roadmaps(current_user.id)


@router.post(
    "/roadmaps/adapt",
    response_model=CareerRoadmapOut,
    summary="Run closed-loop adaptation to pivot career strategy and increment roadmap version",
)
def adapt_roadmap(
    reason: str = Query("Closed-loop execution velocity adaptation", description="Reason for plan adaptation"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.adapt_active_roadmap(db, current_user.id, reason)


@router.get(
    "/progress",
    response_model=CareerProgressMetricsOut,
    summary="Get hard progress metrics (task completion rate, interview scores, application response rate)",
)
def get_progress_metrics(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.get_progress_metrics(db, current_user.id)


@router.post(
    "/coach",
    response_model=CareerCoachResponse,
    summary="Interactive AI Career Coach backed by LangGraph state and user progress context",
)
def talk_to_coach(
    payload: CareerCoachQuery,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.talk_to_coach(db, current_user.id, payload.message)
