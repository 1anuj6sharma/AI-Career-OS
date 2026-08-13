from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class PortfolioAgent:
    """
    Agent 1: Portfolio Agent
    Generates role-adapted portfolio structure, bio, positioning, and project ordering.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, target_role: str, user_skills: List[str]) -> Dict[str, Any]:
        prompt = f"""
        Act as a Senior Executive Career Strategist.
        Design a role-tailored professional portfolio layout for a candidate targeting '{target_role}':

        Candidate Skills: {user_skills}

        Generate:
        - Portfolio Title
        - Executive Bio Statement
        - Strategic Project Positioning Strategy
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "PortfolioAgent",
            "title": f"Professional Portfolio — {target_role}",
            "bio": f"Results-oriented {target_role} specializing in scalable microservice architectures, asynchronous APIs, and cloud-native backend infrastructure.",
            "target_role": target_role,
            "details": getattr(response, "content", str(response)),
        }
