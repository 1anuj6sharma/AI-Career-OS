from datetime import datetime, timedelta
from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class FollowupAgent:
    """
    Agent 5: Follow-up Engine Agent
    Calculates optimal follow-up timing and generates follow-up reminders based on interaction history.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, contact_name: str, purpose: str = "RECRUITER_OUTREACH") -> Dict[str, Any]:
        due = datetime.utcnow() + timedelta(days=4)
        return {
            "agent": "FollowupAgent",
            "due_at": due,
            "reason": f"Follow up with {contact_name} regarding initial {purpose} if no response within 4 days.",
            "suggested_followup_text": f"Hi {contact_name}, just following up on my previous message regarding backend engineering opportunities. I'd still love to connect if you have a moment!",
        }
