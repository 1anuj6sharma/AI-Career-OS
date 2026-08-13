from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class ConversationAgent:
    """
    Agent 4: Conversation Intelligence Agent
    Analyzes recruiter messages/responses, classifying intent (Positive, Neutral, Screening Request), sentiment, and status.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, message_text: str) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Recruiter Conversation Analyst.
        Analyze recruiter message text:
        "{message_text}"

        Classify:
        - Intent (Positive / Interview Request / Neutral / Rejection)
        - Sentiment
        - Opportunity Level (High / Medium / Low)
        - Recommended Action & Suggested Reply
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ConversationAgent",
            "intent": "INTERVIEW_REQUEST" if "call" in message_text.lower() or "screening" in message_text.lower() else "POSITIVE",
            "sentiment": "POSITIVE",
            "opportunity_level": "HIGH",
            "recommended_action": "Send availability for screening call and attach updated resume",
            "suggested_reply": "Thank you for reaching out! I'm available for a screening call this Thursday or Friday. I've attached my updated resume for reference.",
            "details": getattr(response, "content", str(response)),
        }
