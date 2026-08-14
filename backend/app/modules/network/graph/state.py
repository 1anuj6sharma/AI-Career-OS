from typing import TypedDict, Optional, Dict, Any, List


class NetworkingState(TypedDict, total=False):
    user_id: int
    career_goal: Dict[str, Any]
    target_opportunities: List[Dict[str, Any]]
    target_companies: List[str]
    contacts: List[Dict[str, Any]]
    relationship_assessments: List[Dict[str, Any]]
    referral_opportunities: List[Dict[str, Any]]
    networking_strategy: Dict[str, Any]
    outreach_messages: List[Dict[str, Any]]
    approval_status: str  # PENDING, APPROVED, REJECTED
    interaction_results: List[Dict[str, Any]]
    followups: List[Dict[str, Any]]
    brand_analysis: Dict[str, Any]
    errors: List[str]
