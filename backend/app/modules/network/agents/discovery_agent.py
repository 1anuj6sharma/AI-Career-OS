from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class NetworkDiscoveryAgent:
    """
    Agent 1: Network Discovery Agent
    Finds and ranks relevant recruiters, hiring managers, and employees for a target company or job opportunity.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, company_name: str, target_role: str = "Software Engineer") -> List[Dict[str, Any]]:
        return [
            {
                "name": f"Rahul Sharma",
                "role": f"Technical Recruiter @ {company_name}",
                "company": company_name,
                "relevance_score": 94.0,
                "reason": "Direct technical recruiter for backend and platform engineering roles.",
            },
            {
                "name": f"Priya Patel",
                "role": f"Engineering Manager @ {company_name}",
                "company": company_name,
                "relevance_score": 88.0,
                "reason": "Hiring manager for the core backend microservices team.",
            },
        ]
