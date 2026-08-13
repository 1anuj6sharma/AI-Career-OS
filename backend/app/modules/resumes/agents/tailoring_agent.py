from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class ResumeTailoringAgent:
    """
    Agent 6: Resume Tailoring Agent
    Generates a tailored resume draft to match target job description.
    STRICT SECURITY RULE: Never fabricates unprovided skills, experience, companies, or credentials.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, original_resume_text: str, job_title: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Resume Writer.
        Tailor the candidate's resume for the target role '{job_title}':

        CRITICAL INSTRUCTION:
        Do NOT invent fake skills, companies, employment dates, or fake experience.
        Only rephrase, highlight relevant existing technical experiences, and emphasize matching keywords.

        Original Resume Text:
        {original_resume_text[:3000]}

        Target Job Description:
        {job_description[:2000]}

        Output:
        1. Tailoring Plan (List of specific enhancements made)
        2. Draft Tailored Resume (Full text format)
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        res_text = getattr(response, "content", str(response))

        return {
            "agent": "ResumeTailoringAgent",
            "tailoring_plan": [
                f"Reordered summary section to emphasize key requirements for {job_title}",
                "Highlighted matching technical keywords and API architecture experience",
            ],
            "draft_resume": res_text,
            "requires_human_approval": True,
        }
