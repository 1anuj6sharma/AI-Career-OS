from typing import TypedDict, Optional, Dict, Any, List


class OpportunityState(TypedDict, total=False):
    user_id: int
    job_id: int
    raw_job_description: str
    parsed_job: Dict[str, Any]
    user_profile: Dict[str, Any]
    skills: List[str]
    projects: List[Dict[str, Any]]
    resume: Dict[str, Any]
    
    opportunities: List[Dict[str, Any]]
    selected_opportunity: Dict[str, Any]
    company_research: Dict[str, Any]
    opportunity_score: float
    opportunity_score_data: Dict[str, Any]
    
    application_strategy: Dict[str, Any]
    resume_version: Dict[str, Any]
    cover_letter: str
    
    approval_status: str  # PENDING, APPROVED, REJECTED
    application_status: str  # PREPARED, PENDING_APPROVAL, SUBMITTED
    application_id: Optional[int]
    
    feedback: Dict[str, Any]
    errors: List[str]
    current_node: str
    approval_required: bool
