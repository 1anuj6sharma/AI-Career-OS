from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class JobParseQuery(BaseModel):
    company_name: str = Field("TechCorp", example="TechCorp")
    title: str = Field("Senior Python Backend Engineer", example="Senior Python Backend Engineer")
    description: str = Field(..., min_length=20, example="We are looking for a Senior Backend Engineer proficient in Python, FastAPI, PostgreSQL, and Docker. Experience with AWS is preferred.")


class JobRequirementsOut(BaseModel):
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: float
    education_level: str
    responsibilities: List[str]


class JobMatchBreakdownOut(BaseModel):
    skill_match: float
    experience_match: float
    project_match: float
    resume_match: float
    career_match: float
    overall_match: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []


class ApplicationReadinessOut(BaseModel):
    job_id: int
    readiness_score: float
    recommendation: str  # APPLY NOW, PREPARE THEN APPLY, PREPARE FIRST
    priority: str
    estimated_preparation_hours: int
    reason: str


class ApplicationStrategyOut(BaseModel):
    job_id: int
    recommendation: str
    resume_adjustments: List[str] = []
    portfolio_highlights: List[str] = []
    skill_gaps_to_address: List[str] = []
    estimated_preparation_hours: int


class JobOpportunityOut(BaseModel):
    id: int
    source: str
    company_name: str
    title: str
    description: str
    location: Optional[str] = None
    remote_status: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    employment_type: str
    created_at: datetime
    latest_match: Optional[JobMatchBreakdownOut] = None
    latest_readiness: Optional[ApplicationReadinessOut] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyIntelligenceOut(BaseModel):
    company_name: str
    technology_fit: float
    career_growth: float
    overall_fit: float
    analysis_summary: str
