from typing import TypedDict, Optional, Dict, Any, List
from app.modules.resumes.schemas import StructuredResumeData


class ResumeGraphState(TypedDict, total=False):
    user_id: int
    resume_id: int
    raw_text: str
    structured_data: Optional[Dict[str, Any]]
    target_job_id: Optional[int]
    job_description: Optional[str]
    resume_analysis: Optional[Dict[str, Any]]
    ats_analysis: Optional[Dict[str, Any]]
    job_match_analysis: Optional[Dict[str, Any]]
    skill_gap_analysis: Optional[Dict[str, Any]]
    tailoring_plan: Optional[List[str]]
    draft_resume: Optional[str]
    fact_check_passed: bool
    requires_human_approval: bool
    approval_status: str  # PENDING, APPROVED, REJECTED
    errors: List[str]
