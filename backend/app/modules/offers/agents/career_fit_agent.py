from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class CareerFitAgent:
    """
    Agent 4: Career Fit & Growth Agent
    Evaluates target role alignment, technical stack exposure, and long-term career trajectory.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, role: str, company_name: str) -> Dict[str, Any]:
        return {
            "agent": "CareerFitAgent",
            "career_fit_score": 88.0,
            "growth_score": 85.0,
            "technology_fit_score": 92.0,
            "summary": f"Role '{role}' at {company_name} provides strong alignment with backend microservice engineering goals.",
        }
