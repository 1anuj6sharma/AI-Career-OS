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
    external_job_id: Optional[str] = None
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


# ============================================================================
# MODULE 14 — OPPORTUNITY ACQUISITION & APPLICATION SCHEMAS
# ============================================================================

class OpportunityCreate(BaseModel):
    company_name: str = Field(..., example="Stripe")
    title: str = Field(..., example="Senior Backend Engineer")
    description: str = Field(..., example="Build resilient payments APIs using Python, FastAPI, and Postgres")
    location: Optional[str] = Field("Remote", example="Remote")
    remote_status: str = Field("REMOTE", example="REMOTE")
    salary_min: Optional[float] = Field(140000, example=140000)
    salary_max: Optional[float] = Field(180000, example=180000)
    source: str = Field("LINKEDIN", example="LINKEDIN")
    external_job_id: Optional[str] = Field(None, example="job_stripe_9921")


class OpportunityScoreOut(BaseModel):
    id: int
    opportunity_id: int
    skill_score: float
    experience_score: float
    career_alignment_score: float
    compensation_score: float
    growth_score: float
    company_score: float
    overall_score: float
    reasoning: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationPrepareQuery(BaseModel):
    opportunity_id: int = Field(..., example=1)
    target_role: Optional[str] = Field(None, example="Senior Backend Engineer")


class ApplicationApprovalPayload(BaseModel):
    notes: Optional[str] = Field(None, example="Approved by candidate for automated submission")


class ApplicationEventOut(BaseModel):
    id: int
    application_id: int
    event_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationDocumentOut(BaseModel):
    id: int
    application_id: int
    document_type: str
    content_text: Optional[str] = None
    document_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    status: str
    applied_at: Optional[datetime] = None
    source: str
    external_application_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    opportunity: Optional[JobOpportunityOut] = None
    events: List[ApplicationEventOut] = []
    documents: List[ApplicationDocumentOut] = []

    model_config = ConfigDict(from_attributes=True)


class ApplicationFeedbackOut(BaseModel):
    id: int
    user_id: int
    analysis_summary: str
    insights_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityAcquisitionDashboardOut(BaseModel):
    total_opportunities_discovered: int
    high_priority_matches_count: int
    applications_prepared_count: int
    applications_submitted_count: int
    interviews_scheduled_count: int
    recommended_opportunities: List[JobOpportunityOut] = []
    active_applications: List[ApplicationOut] = []
