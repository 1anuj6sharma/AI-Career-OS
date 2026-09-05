from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExecutionPlanBase(BaseModel):
    action: str
    reason: Optional[str] = None
    priority: int = 1
    expected_impact: Optional[str] = None

class ExecutionPlanCreate(ExecutionPlanBase):
    pass

class ExecutionPlanResponse(ExecutionPlanBase):
    id: int
    status: str
    source: str
    created_at: datetime
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ApprovalQueueBase(BaseModel):
    action_type: str
    title: str
    description: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class ApprovalQueueCreate(ApprovalQueueBase):
    pass

class ApprovalQueueResponse(ApprovalQueueBase):
    id: int
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CareerMemoryBase(BaseModel):
    event_type: str
    description: str
    source: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class CareerMemoryCreate(CareerMemoryBase):
    pass

class CareerMemoryResponse(CareerMemoryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class CareerHealthScore(BaseModel):
    score: int
    goal_progress: int
    readiness: int
    opportunity_fit: int
    execution: int
    bottleneck: str
    ai_priority: str

class OpportunityMatch(BaseModel):
    title: str
    company: str
    match_score: int
    verified_skills: List[str]
    missing_skills: List[str]
    recommendation: str

class AgentTelemetry(BaseModel):
    agent_name: str
    status: str
    last_event: str
    timestamp: str

class DashboardSummaryResponse(BaseModel):
    career_health: CareerHealthScore
    execution_plan: List[ExecutionPlanResponse]
    approvals: List[ApprovalQueueResponse]
    opportunities: List[OpportunityMatch]
    agent_activity: List[AgentTelemetry]
    career_memory: List[CareerMemoryResponse]

class NextActionResponse(BaseModel):
    action: str
    reason: str
    priority: int
    expected_impact: str
    estimated_effort: str
    confidence: int
