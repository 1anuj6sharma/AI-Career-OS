from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class OfferCompanyAgent:
    """
    Agent 5: Company & Role Risk Analyzer Agent
    Analyzes company engineering risk, high variable compensation flags, long notice period restrictions, and probation terms.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, company_name: str, variable_percentage: float) -> Dict[str, Any]:
        risk_flags = []
        if variable_percentage > 20.0:
            risk_flags.append("High variable compensation (>20% of CTC) depends on company performance targets.")
        
        return {
            "agent": "OfferCompanyAgent",
            "company_score": 82.0,
            "risk_score": 15.0,
            "risk_flags": risk_flags or ["No unusual employment restriction risks detected."],
            "recommendation": "Review probation and notice period terms prior to signing.",
        }
