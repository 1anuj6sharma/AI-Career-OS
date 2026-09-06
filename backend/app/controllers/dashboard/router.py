from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.controllers.auth.dependencies import get_current_user
from .service import DashboardService
from app.views.dashboard import DashboardSummaryResponse, NextActionResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard Command Center"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Aggregates all Dashboard data: Health Score, Execution Plan, Approvals, Opportunities, Telemetry."""
    service = DashboardService(db)
    return service.get_summary(current_user["id"])

@router.post("/next-action", response_model=NextActionResponse)
def generate_next_action(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Triggers LangGraph/LLM to evaluate Career State and generate the highest ROI action."""
    service = DashboardService(db)
    result = service.generate_next_action(current_user["id"])
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/actions/{action_id}/complete")
def complete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Marks an execution plan action as completed and logs to Career Memory."""
    service = DashboardService(db)
    if not service.complete_action(action_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Action not found")
    return {"status": "success", "message": "Action completed"}

@router.post("/actions/{action_id}/skip")
def skip_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Marks an execution plan action as skipped and triggers AI re-evaluation."""
    service = DashboardService(db)
    if not service.skip_action(action_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Action not found")
    return {"status": "success", "message": "Action skipped"}
