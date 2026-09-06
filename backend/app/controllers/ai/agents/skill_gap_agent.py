from typing import Dict, Any
from sqlalchemy.orm import Session
from app.controllers.ai.tools.profile_tools import get_user_profile_data
from app.controllers.ai.tools.job_tools import get_job_data
from app.controllers.ai.services.llm_service import LLMService


class SkillGapAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, job_id: int = None) -> Dict[str, Any]:
        profile = get_user_profile_data(db, user_id)
        
        if job_id:
            job = get_job_data(db, user_id, job_id)
            target = f"Target Job Title: {job.get('title')}\nJob Description: {job.get('description')}"
        else:
            target = f"Target Role: {profile.get('target_role')}\nThis is a general career gap analysis, not specific to a single job posting."

        prompt = f"""
        Act as a Senior Developer Mentor and Skill Analyst.
        Compare candidate skills against requirements:

        Candidate Skills: {profile.get('skills')}
        {target}

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
