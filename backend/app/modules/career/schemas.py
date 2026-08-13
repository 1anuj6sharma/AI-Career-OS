from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CareerTaskSchema(BaseModel):
    title: str = Field(..., example="Docker & Containerization Mastery")
    description: str = Field(..., example="Build multi-stage Dockerfile and containerize FastAPI project")
    priority: str = Field("HIGH", example="HIGH")
    estimated_minutes: int = Field(60, example=60)


class CareerMilestoneSchema(BaseModel):
    title: str = Field(..., example="Backend Infrastructure Competency")
    description: Optional[str] = None
    target_date: Optional[str] = "Week 2"
    tasks: List[CareerTaskSchema] = []


class CareerRoadmapSchema(BaseModel):
    target_role: str = Field(..., example="Senior Python Backend Engineer")
    objective: str = Field(..., example="Transition from Junior to Senior Backend Engineer specializing in scalable APIs")
    milestones: List[CareerMilestoneSchema] = []


class CareerMilestoneOut(BaseModel):
    id: int
    roadmap_id: int
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None
    status: str
    priority: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerAdaptationOut(BaseModel):
    id: int
    roadmap_id: int
    version_number: int
    reason: str
    adaptation_summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerRoadmapOut(BaseModel):
    id: int
    user_id: int
    target_role: str
    objective: str
    status: str
    version: int
    roadmap_data: Optional[Dict[str, Any]] = None
    milestones: List[CareerMilestoneOut] = []
    adaptations: List[CareerAdaptationOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerProgressMetricsOut(BaseModel):
    task_completion_rate: float
    total_tasks: int
    completed_tasks: int
    interview_score_avg: float
    application_response_rate: float
    active_roadmap_version: int
    skill_proficiency_index: float


class CareerCoachQuery(BaseModel):
    message: str = Field(..., example="What should I focus on today to accelerate my job hunt?")


class CareerCoachResponse(BaseModel):
    reply: str
    recommended_tasks: List[str] = []
    adaptation_recommended: bool = False
