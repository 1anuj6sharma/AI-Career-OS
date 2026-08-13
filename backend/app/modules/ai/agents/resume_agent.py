from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.tools.profile_tools import get_user_profile_data
from app.modules.ai.services.llm_service import LLMService


class ResumeAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, target_job_description: str = None) -> Dict[str, Any]:
        profile = get_user_profile_data(db, user_id)

        prompt = f"""
        Act as an ATS Resume Specialist and Career Coach.
        Analyze candidate experience and suggest tailored resume improvements:

        Candidate Experience: {profile.get('experiences')}
        Skills: {profile.get('skills')}
        Target Job Context: {target_job_description or 'General Senior Engineering Roles'}

        Identify:
        1. Action Verbs & Impact Metrics to add
        2. Missing ATS Keywords
        3. Structural Bullet-Point Improvements
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ResumeAgent",
            "suggestions": getattr(response, "content", str(response)),
            "requires_human_approval": True,
        }
