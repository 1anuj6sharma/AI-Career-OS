from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class AIChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    job_id: Optional[int] = None


class AIChatResponse(BaseModel):
    conversation_id: int
    intent: str
    reply: str
    agent_results: Optional[Dict[str, Any]] = None
    pending_actions: Optional[List[Dict[str, Any]]] = None


class JobMatchRequest(BaseModel):
    job_id: int


class InterviewPrepRequest(BaseModel):
    job_id: int


class PendingActionApproveRequest(BaseModel):
    approve: bool


class PendingActionOut(BaseModel):
    id: int
    action_type: str
    description: str
    payload: Dict[str, Any]
    is_approved: bool
    is_executed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIRunOut(BaseModel):
    id: int
    workflow_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    model: Optional[str] = None
    tokens_used: int
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
