from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class StructuredResumeData(BaseModel):
    personal_information: Dict[str, Any] = Field(default_factory=dict)
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class ResumeVersionOut(BaseModel):
    id: int
    resume_id: int
    version_number: int
    version_name: str
    parent_version_id: Optional[int] = None
    created_by: str
    generation_reason: Optional[str] = None
    job_id: Optional[int] = None
    change_summary: Optional[str] = None
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeOut(BaseModel):
    id: int
    user_id: int
    name: str
    original_filename: str
    file_url: Optional[str] = None
    file_type: str
    status: str
    versions: List[ResumeVersionOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeAnalysisOut(BaseModel):
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    career_alignment: str
    details: str


class ATSAnalysisOut(BaseModel):
    keyword_coverage_percent: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    section_issues: List[str]
    semantic_alignment_score: float
    recommendations: List[str]


class TailoringPlanOut(BaseModel):
    tailoring_plan: List[str]
    draft_resume: str
    fact_check_passed: bool
    requires_human_approval: bool
