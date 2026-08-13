from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class NetworkingCoachAgent:
    """
    Agent 6: Networking Coach Agent
    User-facing conversational coach providing grounded networking advice and contact recommendations for target jobs.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, message: str, user_network_context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Networking Coach.
        Provide grounded networking advice for candidate question:

        User Question: "{message}"
        Network Context: {user_network_context}

        Provide actionable recommendations on outreach strategy and follow-up etiquette.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "NetworkingCoachAgent",
            "reply": getattr(response, "content", str(response)),
        }
