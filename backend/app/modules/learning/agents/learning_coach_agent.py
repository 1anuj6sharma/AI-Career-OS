from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class LearningCoachAgent:
    """
    Agent 7: Learning Coach Agent
    Connects study time, completed modules, and assessment progress with broader Module 7 execution goals.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, user_learning_context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Learning Coach.
        Synthesize study time and skill progress for candidate:

        Learning Context: {user_learning_context}

        Provide coaching message connecting study tasks to upcoming job applications and interview readiness.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "LearningCoachAgent",
            "coaching_message": getattr(response, "content", str(response)),
        }
