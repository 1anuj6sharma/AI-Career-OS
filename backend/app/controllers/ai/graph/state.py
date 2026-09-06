from typing import TypedDict, Optional, List, Dict, Any


class CareerGraphState(TypedDict, total=False):
    user_id: int
    conversation_id: Optional[int]
    user_request: str
    intent: str
    job_id: Optional[int]
    profile_data: Optional[Dict[str, Any]]
    job_data: Optional[Dict[str, Any]]
    agent_results: Dict[str, Any]
    tool_results: List[Dict[str, Any]]
    pending_actions: List[Dict[str, Any]]
    final_response: str
