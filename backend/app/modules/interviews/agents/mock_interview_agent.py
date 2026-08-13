from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class MockInterviewAgent:
    """
    Agent 5: Mock Interview Agent
    Main user-facing AI interviewer managing conversation state and asking follow-ups.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        question_text: str,
        user_answer: str = "",
        previous_eval: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as a Professional AI Technical Interviewer conducting a live mock interview.

        Current Question: {question_text}
        Candidate Answer: {user_answer}

        Provide a supportive, professional interviewer response that asks an insightful follow-up question or transitions to the next technical topic.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "MockInterviewAgent",
            "interviewer_response": getattr(response, "content", str(response)),
        }
