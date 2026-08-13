from typing import TypedDict, Optional, Dict, Any, List


class NetworkingState(TypedDict, total=False):
    user_id: int
    opportunity_id: Optional[int]
    company_id: Optional[int]
    contact_id: Optional[int]
    user_profile: Dict[str, Any]
    career_goal: Dict[str, Any]
    job: Dict[str, Any]
    contact_profile: Dict[str, Any]
    relationship: Dict[str, Any]
    previous_interactions: List[Dict[str, Any]]
    outreach_intent: Optional[str]
    outreach_message: Optional[Dict[str, Any]]
    approval_status: str
    response: Optional[Dict[str, Any]]
    response_classification: Optional[Dict[str, Any]]
    next_action: Optional[str]
    follow_up_date: Optional[str]
    errors: List[str]
    retry_count: int
    failed_tools: List[str]
    partial_results: Dict[str, Any]
