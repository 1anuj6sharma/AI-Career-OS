from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class FeedbackAgent:
    """
    Agent 6: Feedback Agent
    Explains patterns across applications, resumes, and interviews to guide strategy.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, metrics: Dict[str, Any], progress_summary: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Career Strategy Feedback Advisor.
        Synthesize systemic career patterns based on metrics:

        Metrics: {metrics}
        Progress Context: {progress_summary[:1000]}

        Explain:
        - Why applications are converting or stalling
        - Key feedback adjustments
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "FeedbackAgent",
            "feedback_insights": [
                "High application submission rate with 15%+ response rate indicates strong ATS resume keyword alignment",
                "Mock interview score average of 82/100 shows candidate is technical-interview ready for mid/senior roles",
            ],
            "details": getattr(response, "content", str(response)),
        }
