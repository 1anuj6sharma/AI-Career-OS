from typing import TypedDict, Optional, Dict, Any, List


class CareerExecutionState(TypedDict, total=False):
    user_id: int
    career_goal: Dict[str, Any]
    current_skills: List[str]
    required_skills: List[str]
    skill_gaps: List[Dict[str, Any]]
    roadmap: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    application_metrics: Dict[str, Any]
    interview_metrics: Dict[str, Any]
    progress_metrics: Dict[str, Any]
    feedback: List[str]
    recommendations: List[str]
    adaptation_required: bool
    next_action: str
    errors: List[str]
