from typing import TypedDict, Optional, Dict, Any, List


class InterviewState(TypedDict, total=False):
    interview_id: int
    user_id: int
    job_id: Optional[int]
    resume_version_id: Optional[int]
    interview_type: str
    questions: List[Dict[str, Any]]
    current_question_index: int
    current_question: Optional[Dict[str, Any]]
    current_answer: Optional[str]
    answer_history: List[Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]
    topics_covered: List[str]
    difficulty: str
    overall_score: Optional[float]
    next_action: Optional[str]
    interview_complete: bool
    requires_human_input: bool
