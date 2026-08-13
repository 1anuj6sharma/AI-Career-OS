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
    skill_match: Dict[str, Any]
    experience_match: Dict[str, Any]
    project_match: Dict[str, Any]
    resume_match: Dict[str, Any]
    career_match: Dict[str, Any]
    location_match: Dict[str, Any]
    compensation_match: Dict[str, Any]
    growth_match: Dict[str, Any]
    match_score: Optional[float]
    readiness_score: Optional[float]
    skill_gaps: List[str]
    risks: List[str]
    application_strategy: Dict[str, Any]
    recommendation: str
    errors: List[str]
    current_node: str
    retry_count: int
    failed_sources: List[str]
    partial_results: Dict[str, Any]
    approval_required: bool
