from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.tools.profile_tools import get_user_profile_data
from app.modules.ai.tools.application_tools import get_active_applications_data
from app.modules.ai.services.llm_service import LLMService


class CareerStrategistAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int) -> Dict[str, Any]:
        profile = get_user_profile_data(db, user_id)
        applications = get_active_applications_data(db, user_id)

        prompt = f"""
        Act as a Senior Executive Career Strategist.
        Analyze the following candidate profile and job search pipeline:

        Profile: {profile}
        Applications: {applications}

        Provide a structured strategy response with:
        1. Executive Career Summary
        2. Top Strengths & Competitive Advantage
        3. Key Vulnerabilities / Risks
        4. High-Impact Strategic Recommendations
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "CareerStrategistAgent",
            "summary": getattr(response, "content", str(response)),
            "profile_used": profile.get("full_name"),
            "applications_count": len(applications),
        }
