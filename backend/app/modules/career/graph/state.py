from typing import TypedDict, Optional, Dict, Any, List


class CareerPerformanceState(TypedDict, total=False):
    user_id: int
    career_goal: Dict[str, Any]
    current_role: Dict[str, Any]
    target_role: Dict[str, Any]
    skills: List[Dict[str, Any]]
    skill_gaps: List[Dict[str, Any]]
    active_goals: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    progress_metrics: Dict[str, Any]
    performance_score: float
    blockers: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    market_changes: List[Dict[str, Any]]
    recommended_actions: List[str]
    updated_roadmap: Dict[str, Any]
    next_review_date: Optional[str]
    errors: List[str]


# Backward compatibility alias
CareerExecutionState = CareerPerformanceState
