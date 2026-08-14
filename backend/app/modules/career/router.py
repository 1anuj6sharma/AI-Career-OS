from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
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
    CareerGoalCreate,
    CareerGoalOut,
    CareerTaskCreate,
    CareerTaskOut,
    SkillProgressOut,
    CareerReviewCreate,
    CareerReviewOut,
    CareerRiskOut,
    CareerScenarioCreate,
    CareerScenarioOut,
    CareerPerformanceDashboardOut,
)

router = APIRouter(prefix="/career", tags=["Module 13 — AI Career Performance, Productivity & Continuous Growth Engine"])


# ----------------------------------------------------------------------------
# Roadmap & Adaptations
# ----------------------------------------------------------------------------
@router.post(
    "/roadmaps/generate",
    response_model=CareerRoadmapOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new versioned career roadmap",
)
def generate_roadmap(
    target_role: Optional[str] = Query(None, description="Target career role"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.generate_roadmap(db, current_user.id, target_role)


@router.get(
    "/roadmaps/active",
    response_model=Optional[CareerRoadmapOut],
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


# ----------------------------------------------------------------------------
# Module 13 — Goals Management
# ----------------------------------------------------------------------------
@router.post(
    "/goals",
    response_model=CareerGoalOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new career goal",
)
def create_goal(
    payload: CareerGoalCreate,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.create_goal(current_user.id, payload)


@router.get(
    "/goals",
    response_model=List[CareerGoalOut],
    summary="List user career goals",
)
def list_goals(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_goals(current_user.id, status_filter)


@router.patch(
    "/goals/{goal_id}/status",
    response_model=CareerGoalOut,
    summary="Update goal status (ACTIVE, COMPLETED, ARCHIVED)",
)
def update_goal_status(
    goal_id: int,
    new_status: str = Query(..., example="COMPLETED"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    goal = service.update_goal_status(goal_id, current_user.id, new_status)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete(
    "/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a career goal",
)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    success = service.delete_goal(goal_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return None


# ----------------------------------------------------------------------------
# Module 13 — Tasks Management
# ----------------------------------------------------------------------------
@router.post(
    "/tasks",
    response_model=CareerTaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new career task linked to milestone/goal",
)
def create_task(
    payload: CareerTaskCreate,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.create_task(current_user.id, payload)


@router.get(
    "/tasks",
    response_model=List[CareerTaskOut],
    summary="List user career tasks",
)
def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_tasks(current_user.id, status_filter)


@router.patch(
    "/tasks/{task_id}/status",
    response_model=CareerTaskOut,
    summary="Update task status (PENDING, IN_PROGRESS, COMPLETED, POSTPONED)",
)
def update_task_status(
    task_id: int,
    task_status: str = Query(..., alias="status", example="COMPLETED"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    task = service.update_task_status(task_id, current_user.id, task_status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ----------------------------------------------------------------------------
# Module 13 — Dashboard & Performance Intelligence
# ----------------------------------------------------------------------------
@router.get(
    "/dashboard",
    response_model=CareerPerformanceDashboardOut,
    summary="Get unified Module 13 Performance & Continuous Growth Dashboard",
)
def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.get_performance_dashboard(db, current_user.id)


@router.get(
    "/skills/progress",
    response_model=List[SkillProgressOut],
    summary="List skill progression matrix",
)
def list_skill_progress(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_skill_progress(current_user.id)


@router.get(
    "/reviews",
    response_model=List[CareerReviewOut],
    summary="List historical career reviews",
)
def list_reviews(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_reviews(current_user.id)


@router.post(
    "/reviews",
    response_model=CareerReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate weekly or monthly career review",
)
def generate_review(
    review_type: str = Query("WEEKLY", description="DAILY, WEEKLY, MONTHLY, MILESTONE"),
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.generate_review(db, current_user.id, review_type)


@router.get(
    "/risks",
    response_model=List[CareerRiskOut],
    summary="List active career risk signals",
)
def list_risks(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_active_risks(current_user.id)


@router.post(
    "/scenarios",
    response_model=CareerScenarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Simulate alternative career path scenario",
)
def simulate_scenario(
    payload: CareerScenarioCreate,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.simulate_scenario(current_user.id, payload.scenario_name, payload.target_role, payload.assumptions)


@router.get(
    "/scenarios",
    response_model=List[CareerScenarioOut],
    summary="List saved career scenarios",
)
def list_scenarios(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    return service.list_scenarios(current_user.id)


# ----------------------------------------------------------------------------
# AI Endpoints
# ----------------------------------------------------------------------------
@router.post(
    "/coach",
    response_model=CareerCoachResponse,
    summary="Interactive AI Career Coach backed by persistent Career Performance State",
)
def talk_to_coach(
    payload: CareerCoachQuery,
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    return service.talk_to_coach(db, current_user.id, payload.message)


@router.post(
    "/ai/plan",
    summary="AI Daily/Weekly Productivity Plan Generation",
)
def generate_ai_daily_plan(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
):
    agent = service.graph_orchestrator.productivity_agent
    return agent.run({"user_id": current_user.id})


@router.post(
    "/ai/analyze-progress",
    summary="AI Progress Performance Analysis",
)
def analyze_ai_progress(
    current_user: User = Depends(get_current_active_user),
    service: CareerService = Depends(get_career_service),
    db: Session = Depends(get_db),
):
    perf_data = service.perf_service.calculate_performance_score(db, current_user.id)
    agent = service.graph_orchestrator.performance_agent
    return agent.run(perf_data)
