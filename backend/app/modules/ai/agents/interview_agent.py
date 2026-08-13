from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.tools.job_tools import get_job_data
from app.modules.ai.tools.profile_tools import get_user_profile_data
from app.modules.ai.services.llm_service import LLMService


class InterviewAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, job_id: int) -> Dict[str, Any]:
        job = get_job_data(db, user_id, job_id)
        profile = get_user_profile_data(db, user_id)

        prompt = f"""
        Act as a Principal Engineer & Technical Interviewer for {job.get('company_name', 'Company')}.
        Generate an interview preparation kit for:

        Role: {job.get('title')}
        Location: {job.get('location')}
        Description: {job.get('description')}
        Candidate Profile: {profile.get('current_role')}, Skills: {profile.get('skills')}

        Provide 5 tailored preparation modules:
        1. 3 Technical System Design / Architecture Questions
        2. 3 Data Structures & Algorithms (DSA) Focus Topics
        3. 3 Behavioral Questions (STAR Method)
        4. 2 Company / Product Specific Questions
        5. 3 Smart Questions for Candidate to Ask Interviewer
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "InterviewAgent",
            "job_id": job_id,
            "job_title": job.get("title"),
            "company_name": job.get("company_name"),
            "preparation_kit": getattr(response, "content", str(response)),
        }
