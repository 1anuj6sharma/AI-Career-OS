from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.master_orchestrator.dependencies import get_master_orchestrator_service
from app.modules.master_orchestrator.service import MasterOrchestratorService
from app.modules.master_orchestrator.schemas import (
    CommandCenterQuery,
    NextBestActionOut,
    MasterCareerPlanOut,
    MasterCareerStrategyOut,
    MasterApprovalOut,
    CommandCenterDashboardOut,
)

router = APIRouter(prefix="/master-orchestrator", tags=["Module 15 — AI Career OS Master Orchestrator & Autonomous Career Agent"])


@router.post(
    "/chat",
    summary="Conversational Career OS Command Center Interface",
)
def command_center_chat(
    payload: CommandCenterQuery,
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
    db: Session = Depends(get_db),
):
    return service.process_command_center_query(db, current_user.id, payload.message)


@router.get(
    "/next-best-action",
    response_model=NextBestActionOut,
    summary="Get single highest-value action recommendation for candidate",
)
def get_next_best_action(
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
    db: Session = Depends(get_db),
):
    return service.get_next_best_action(db, current_user.id)


@router.get(
    "/dashboard",
    response_model=CommandCenterDashboardOut,
    summary="Get unified Career OS Command Center Dashboard",
)
def get_command_center_dashboard(
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
    db: Session = Depends(get_db),
):
    return service.get_command_center_dashboard(db, current_user.id)


@router.post(
    "/plans",
    response_model=MasterCareerPlanOut,
    status_code=status.HTTP_201_CREATED,
    summary="Decompose goal into Master Plan with milestone DAG steps across modules",
)
def create_master_plan(
    goal_title: str = Query("Senior Backend / AI Engineer", example="Senior Backend / AI Engineer"),
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
):
    return service.create_master_plan(current_user.id, goal_title)


@router.get(
    "/plans/active",
    response_model=Optional[MasterCareerPlanOut],
    summary="Get currently active master career plan",
)
def get_active_plan(
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
):
    return service.get_active_plan(current_user.id)


@router.get(
    "/strategies",
    response_model=List[MasterCareerStrategyOut],
    summary="List master career strategy version history",
)
def list_strategies(
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
):
    return service.list_strategies(current_user.id)


@router.post(
    "/approvals/{approval_id}/approve",
    response_model=MasterApprovalOut,
    summary="Approve Level 3 or Level 4 action",
)
def approve_action(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
):
    app = service.approve_action(current_user.id, approval_id)
    if not app:
        raise HTTPException(status_code=404, detail="Approval record not found")
    return app


@router.post(
    "/approvals/{approval_id}/reject",
    response_model=MasterApprovalOut,
    summary="Reject action",
)
def reject_action(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    service: MasterOrchestratorService = Depends(get_master_orchestrator_service),
):
    app = service.reject_action(current_user.id, approval_id)
    if not app:
        raise HTTPException(status_code=404, detail="Approval record not found")
    return app
