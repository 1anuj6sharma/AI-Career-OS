from typing import TypedDict, Optional, Dict, Any, List


class CareerBrandState(TypedDict, total=False):
    user_id: int
    career_goal: Dict[str, Any]
    target_role: str
    skills: List[str]
    projects: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]
    resume_data: Dict[str, Any]
    github_data: Dict[str, Any]
    linkedin_data: Dict[str, Any]
    portfolio_data: Dict[str, Any]
    brand_analysis: Dict[str, Any]
    visibility_score: float
    recommendations: List[str]
    content_requests: List[Dict[str, Any]]
    optimization_required: bool
    errors: List[str]
    run_id: str
    current_node: str
    retry_count: int
    failed_sources: List[str]
    partial_results: Dict[str, Any]
    approval_required: bool
    checkpoint_id: str
