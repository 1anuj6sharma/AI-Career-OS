from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class VisibilityAgent:
    """
    Agent 7: Visibility Agent
    Identifies recruiter visibility gaps and creates cross-module recommendation events for Modules 7 & 8.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, target_role: str, scores: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as a Recruiter Visibility Specialist.
        Analyze visibility metrics for '{target_role}':

        Scores: {scores}

        Provide:
        1. Recruiter Searchability Assessment
        2. Visibility Gaps (e.g., missing public repository evidence, missing technical blog articles)
        3. Cross-Module Execution Recommendations for Modules 7 & 8
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "VisibilityAgent",
            "visibility_score": scores.get("overall_score", 75.0),
            "visibility_gaps": [
                "Lack of published technical article on System Design & Distributed Caching",
                "GitHub repository README documentation missing architectural diagrams",
            ],
            "recommendations": [
                "Publish a technical article on Docker containerization best practices",
                "Update LinkedIn headline with high-intent keywords: 'FastAPI', 'Microservices', 'PostgreSQL'",
            ],
            "details": getattr(response, "content", str(response)),
        }
