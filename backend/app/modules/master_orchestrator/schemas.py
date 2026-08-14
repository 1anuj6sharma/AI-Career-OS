from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CommandCenterQuery(BaseModel):
    message: str = Field(..., example="I want to get an AI Engineer job in 90 days. What should I do today?")


class NextBestActionOut(BaseModel):
    action_title: str = Field(..., example="Complete System Design Mock Interview")
    description: str = Field(..., example="Your current target role requires stronger system design performance, which is your largest gap.")
    category: str = Field("INTERVIEW_PREP", example="INTERVIEW_PREP")
    target_module: str = Field("module_6", example="module_6")
    expected_impact: str = Field("HIGH", example="HIGH")
    rank_score: float = Field(92.5, example=92.5)
    execution_payload: Optional[Dict[str, Any]] = None


class MasterPlanStepOut(BaseModel):
    id: int
    plan_id: int
    module_name: str
    action_name: str
    status: str
    priority: int
    dependencies_json: Optional[List[str]] = None
    result_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MasterCareerPlanOut(BaseModel):
    id: int
    user_id: int
    goal_title: str
    strategy_summary: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    steps: List[MasterPlanStepOut] = []

    model_config = ConfigDict(from_attributes=True)


class MasterCareerStrategyOut(BaseModel):
    id: int
    user_id: int
    version_number: int
    strategy_title: str
    objective: str
    reasons_for_pivot: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MasterApprovalOut(BaseModel):
    id: int
    user_id: int
    workflow_id: str
    action_type: str
    action_description: str
    risk_level: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CommandCenterDashboardOut(BaseModel):
    user_id: int
    current_goal: str
    current_strategy: MasterCareerStrategyOut
    next_best_action: NextBestActionOut
    career_readiness_pct: float
    performance_score: float
    active_plan: Optional[MasterCareerPlanOut] = None
    pending_approvals: List[MasterApprovalOut] = []
    active_risks_count: int
    top_opportunities_count: int
    recent_events_count: int
