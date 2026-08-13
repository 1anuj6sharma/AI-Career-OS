from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.tools.profile_tools import get_user_profile_data
from app.modules.ai.tools.job_tools import get_job_data
from app.modules.ai.services.llm_service import LLMService


class SkillGapAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, job_id: int) -> Dict[str, Any]:
        profile = get_user_profile_data(db, user_id)
        job = get_job_data(db, user_id, job_id)

        prompt = f"""
        Act as a Senior Developer Mentor and Skill Analyst.
        Compare candidate skills against job requirements:

        Candidate Skills: {profile.get('skills')}
        Target Job Title: {job.get('title')}
        Job Description: {job.get('description')}

        Categorize missing skills into:
        1. High Priority (Must-have for interviews)
        2. Medium Priority (Good to have)
        3. Low Priority (Nice to have)
        
        Provide a 2-week learning action plan.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "SkillGapAgent",
            "job_id": job_id,
            "analysis": getattr(response, "content", str(response)),
        }
