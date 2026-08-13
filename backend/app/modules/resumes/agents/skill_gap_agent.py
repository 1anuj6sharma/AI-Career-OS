from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class ResumeSkillGapAgent:
    """
    Agent 5: Resume Skill Gap Agent
    Categorizes skills into Strong, Partial, and Missing against target job.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, resume_skills: List[str], job_description: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Technical Skill Coach.
        Compare resume skills: {resume_skills} against job requirements: {job_description[:2000]}

        Categorize into:
        - Strong Skills
        - Partial Skills
        - Missing Skills (High, Medium, Low priority)
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ResumeSkillGapAgent",
            "strong_skills": [s for s in resume_skills if s.lower() in job_description.lower()],
            "gap_analysis": getattr(response, "content", str(response)),
        }
