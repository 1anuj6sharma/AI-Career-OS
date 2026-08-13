from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class InterviewCreate(BaseModel):
    title: str = Field(..., example="Amazon Python Backend Engineer Interview")
    company_name: Optional[str] = Field(None, example="Amazon")
    job_id: Optional[int] = None
    resume_version_id: Optional[int] = None
    interview_type: str = Field("TECHNICAL", example="TECHNICAL")
    scheduled_at: Optional[datetime] = None


class AnswerEvaluationOut(BaseModel):
    id: int
    technical_score: Optional[float] = None
    clarity_score: Optional[float] = None
    depth_score: Optional[float] = None
    relevance_score: Optional[float] = None
    overall_score: float
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    missing_points: Optional[List[str]] = None
    feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewAnswerOut(BaseModel):
    id: int
    question_id: int
    answer: str
    duration_seconds: Optional[int] = None
    evaluation: Optional[AnswerEvaluationOut] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewQuestionOut(BaseModel):
    id: int
    interview_id: int
    question: str
    category: str
    topic: Optional[str] = None
    difficulty: str
    expected_time_minutes: int
    evaluation_criteria: Optional[str] = None
    answers: List[InterviewAnswerOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewOut(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    resume_version_id: Optional[int] = None
    title: str
    company_name: Optional[str] = None
    interview_type: str
    scheduled_at: Optional[datetime] = None
    status: str
    overall_score: Optional[float] = None
    questions: List[InterviewQuestionOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewAnswerCreate(BaseModel):
    answer: str = Field(..., min_length=1)
    duration_seconds: Optional[int] = 60


class PreparationPlanOut(BaseModel):
    interview_id: int
    interview_type: str
    priority_topics: List[str]
    behavioral_topics: List[str]
    company_insights: Dict[str, Any]
    preparation_tasks_created: int
    strategy_summary: str


class InterviewReportOut(BaseModel):
    interview_id: int
    title: str
    company_name: Optional[str] = None
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommended_next_steps: List[str]
