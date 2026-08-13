from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class TransitionAgent:
    """
    Agent 8: Career Transition Agent
    Generates 30/60/90-day onboarding and transition plans upon offer acceptance, integrating state with Modules 7, 8 & 9.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, company_name: str, role: str) -> Dict[str, Any]:
        return {
            "agent": "TransitionAgent",
            "company_name": company_name,
            "role": role,
            "plan_30_days": [
                "Understand engineering architecture and microservice boundaries",
                "Set up local development container environment",
                "Complete first bug fix or minor PR contribution",
            ],
            "plan_60_days": [
                "Take ownership of core backend feature module",
                "Optimize database query performance and index strategy",
            ],
            "plan_90_days": [
                "Deliver production feature release independently",
                "Participate in architecture review and system design discussions",
            ],
        }
