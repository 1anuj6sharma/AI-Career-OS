from typing import TypedDict, Optional, Dict, Any, List


class LearningState(TypedDict, total=False):
    user_id: int
    career_goal: Dict[str, Any]
    target_skills: List[str]
    skill_gaps: List[str]
    learning_path: Dict[str, Any]
    current_topic: Optional[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    study_tasks: List[Dict[str, Any]]
    completed_lessons: List[str]
    quiz_results: List[Dict[str, Any]]
    practice_results: List[Dict[str, Any]]
    weak_topics: List[str]
    progress_score: float
    adaptation_required: bool
    next_action: str
