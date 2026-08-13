from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.tools.job_tools import calculate_hybrid_job_match
from app.modules.ai.services.llm_service import LLMService


class JobMatchAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, job_id: int) -> Dict[str, Any]:
        # 1. Deterministic scoring algorithm
        match_data = calculate_hybrid_job_match(db, user_id, job_id)

        prompt = f"""
        Act as a Technical Hiring Manager and Job Fit Specialist.
        Synthesize the deterministic match results for job '{match_data.get('job_title')}' at '{match_data.get('company_name')}':

        Score: {match_data.get('overall_score')}%
        Breakdown: {match_data.get('breakdown')}
        Matched Skills: {match_data.get('matched_skills')}

        Generate a concise, evidence-backed evaluation explaining why this job fits or where skill gaps exist.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        llm_response = llm.invoke(prompt)

        match_data["ai_explanation"] = getattr(llm_response, "content", str(llm_response))
        match_data["agent"] = "JobMatchAgent"
        return match_data
