from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class StrategyAgent:
    """
    Agent 7: Application Strategy Agent
    Generates structured application strategy checklist (resume adjustments, portfolio highlights, preparation time estimate).
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, job_title: str, missing_skills: List[str], readiness_info: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as a Strategic Career Advisor.
        Create an execution checklist for applying to '{job_title}':

        Readiness Recommendation: {readiness_info.get('recommendation')}
        Missing Skills: {missing_skills}

        Generate specific resume adjustments and project highlights.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "StrategyAgent",
            "job_title": job_title,
            "recommendation": readiness_info.get("recommendation", "PREPARE THEN APPLY"),
            "resume_adjustments": [
                "Tailor summary to highlight FastAPI and microservices experience",
                "Emphasize PostgreSQL query performance optimizations",
            ],
            "portfolio_highlights": [
                "Position AI Career OS microservice architecture project at the top",
            ],
            "skill_gaps_to_address": missing_skills,
            "estimated_preparation_hours": readiness_info.get("estimated_preparation_hours", 5),
            "details": getattr(response, "content", str(response)),
        }
