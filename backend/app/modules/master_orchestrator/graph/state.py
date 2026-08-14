from typing import TypedDict, Optional, Dict, Any, List


class MasterCareerState(TypedDict, total=False):
    user_id: int
    intent: Dict[str, Any]
    global_career_state: Dict[str, Any]
    master_plan: Dict[str, Any]
    decomposed_steps: List[Dict[str, Any]]
    routed_modules: List[Dict[str, Any]]
    execution_results: List[Dict[str, Any]]
    reflection: Dict[str, Any]
    adapted_strategy: Dict[str, Any]
    next_best_action: Dict[str, Any]
    approval_required: bool
    approval_level: str  # LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4
    approval_status: str  # PENDING, APPROVED, REJECTED
    errors: List[str]
