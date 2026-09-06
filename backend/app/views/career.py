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
    goal_id: Optional[int] = None
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

    model_config = ConfigDict(from_attributes=True)


class CareerCoachQuery(BaseModel):
    message: str = Field(..., example="What should I focus on today to accelerate my job hunt?")


class CareerCoachResponse(BaseModel):
    reply: str
    recommended_tasks: List[str] = []
    adaptation_recommended: bool = False


# ============================================================================
# MODULE 13 — SCHEMAS FOR GOALS, TASKS, PROGRESS, REVIEWS, RISKS, SCENARIOS
# ============================================================================

class CareerGoalCreate(BaseModel):
    title: str = Field(..., example="Master Production Microservices & Data Engineering")
    description: Optional[str] = Field(None, example="Build scalable FastAPI & Azure Data Factory pipelines")
    goal_type: str = Field("LONG_TERM", example="LONG_TERM")  # LONG_TERM, SHORT_TERM, SKILL_ACQUISITION
    priority: str = Field("HIGH", example="HIGH")
    target_date: Optional[datetime] = None


class CareerGoalOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    goal_type: str
    priority: str
    status: str
    target_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerTaskCreate(BaseModel):
    title: str = Field(..., example="Implement Redis Caching Layer")
    description: Optional[str] = Field(None, example="Add Redis LRU cache to FastAPI backend")
    milestone_id: Optional[int] = None
    goal_id: Optional[int] = None
    priority: str = Field("MEDIUM", example="MEDIUM")
    estimated_minutes: int = Field(45, example=45)
    due_date: Optional[datetime] = None


class CareerTaskOut(BaseModel):
    id: int
    user_id: int
    milestone_id: Optional[int] = None
    goal_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    estimated_minutes: int
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillProgressOut(BaseModel):
    id: int
    user_id: int
    skill_name: str
    confidence_score: float
    evidence_score: float
    assessment_score: float
    project_score: float
    status: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerReviewCreate(BaseModel):
    review_type: str = Field("WEEKLY", example="WEEKLY")  # DAILY, WEEKLY, MONTHLY, MILESTONE
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class CareerReviewOut(BaseModel):
    id: int
    user_id: int
    review_type: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    performance_score: float
    summary: str
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerRiskOut(BaseModel):
    id: int
    user_id: int
    risk_type: str
    severity: str
    description: str
    recommended_action: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerScenarioCreate(BaseModel):
    scenario_name: str = Field(..., example="AI Engineering vs Backend Engineering")
    target_role: str = Field(..., example="AI Systems Engineer")
    assumptions: Optional[Dict[str, Any]] = None


class CareerScenarioOut(BaseModel):
    id: int
    user_id: int
    scenario_name: str
    target_role: str
    assumptions: Optional[Dict[str, Any]] = None
    projection: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerPerformanceDashboardOut(BaseModel):
    user_id: int
    target_role: str
    overall_readiness_score: float
    performance_score: float
    performance_breakdown: Dict[str, float]
    active_goals_count: int
    pending_tasks_count: int
    completed_tasks_count: int
    skills_summary: List[SkillProgressOut]
    active_risks: List[CareerRiskOut]
    recent_review: Optional[CareerReviewOut] = None
    roadmap_version: int
