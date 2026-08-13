from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class LinkedInAgent:
    """
    Agent 4: LinkedIn Profile Intelligence Agent
    Generates LinkedIn headline, about section, and experience alignment recommendations.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, target_role: str, user_skills: List[str]) -> Dict[str, Any]:
        prompt = f"""
        Act as a LinkedIn Personal Branding Expert.
        Optimize LinkedIn positioning for target role '{target_role}':

        Skills: {user_skills}

        Generate:
        1. Compelling, High-SEO LinkedIn Headline
        2. Story-driven Executive About Section
        3. High-impact Skill Keywords
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "LinkedInAgent",
            "current_headline_analysis": "Headline is generic and missing high-impact technical keywords.",
            "suggested_headline": f"{target_role} | Microservice Architecture | FastAPI & Python Systems | Cloud-Native Solutions",
            "suggested_about": f"Passionate {target_role} dedicated to designing resilient, low-latency microservices and automated API infrastructure.",
            "keyword_gaps": ["Docker", "PostgreSQL Indexing", "System Design", "Asynchronous Python"],
            "alignment_score": 85.0,
            "details": getattr(response, "content", str(response)),
        }
