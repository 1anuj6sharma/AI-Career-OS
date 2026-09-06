from typing import TypedDict, Optional, Dict, Any, List


class CareerDecisionState(TypedDict, total=False):
    user_id: int
    offer_id: Optional[int]
    offer_details: Dict[str, Any]
    career_goal: Dict[str, Any]
    user_profile: Dict[str, Any]
    skills: List[str]
    experience: List[Dict[str, Any]]
    market_data: Dict[str, Any]
    company_data: Dict[str, Any]
    alternative_offers: List[Dict[str, Any]]
    compensation_analysis: Dict[str, Any]
    career_fit_analysis: Dict[str, Any]
    growth_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    offer_score: Optional[float]
    negotiation_leverage: Optional[float]
    negotiation_strategy: Optional[Dict[str, Any]]
    decision: Optional[str]
    reasoning: Optional[str]
    confidence: Optional[float]
    user_approval_required: bool
    retry_count: int
    failed_sources: List[str]
    partial_results: Dict[str, Any]
    errors: List[str]
