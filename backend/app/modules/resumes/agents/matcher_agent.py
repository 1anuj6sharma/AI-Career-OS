from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.ai.tools.job_tools import calculate_hybrid_job_match


class ResumeJobMatchAgent:
    """
    Agent 4: Resume Job Match Agent
    Integrates Profile + Job + Resume for comprehensive fit score.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, resume_content: str, job_id: int) -> Dict[str, Any]:
        match = calculate_hybrid_job_match(db, user_id, job_id)

        prompt = f"""
        Act as a Principal Recruiter evaluating resume suitability:
        Job Fit Score: {match.get('overall_score')}%
        Resume Content: {resume_content[:2000]}

        Synthesize the resume match evaluation.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        match["resume_match_details"] = getattr(response, "content", str(response))
        match["agent"] = "ResumeJobMatchAgent"
        return match
