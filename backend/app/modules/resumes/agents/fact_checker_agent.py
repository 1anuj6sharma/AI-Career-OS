from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class FactCheckerAgent:
    """
    Agent 7: Fact Checker Agent
    Verifies that AI tailored resume drafts do not contain fabricated companies, skills, or metrics unsupported by source data.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, original_resume_text: str, draft_resume_text: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Strict Compliance & Fact Verification Auditor.
        Verify if the tailored draft introduces unsupported or hallucinated companies, degrees, dates, or skills.

        Original Resume Evidence:
        {original_resume_text[:2500]}

        Tailored AI Draft:
        {draft_resume_text[:2500]}

        Check:
        1. Are all listed companies authentic to the original?
        2. Are skills grounded in user evidence?
        3. Are numbers or claims truthful rephrasings?

        Return PASS if verified, or FAIL with specific violations.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        res_text = str(getattr(response, "content", response))
        is_pass = "FAIL" not in res_text.upper()

        return {
            "agent": "FactCheckerAgent",
            "passed": is_pass,
            "verification_details": res_text,
        }
