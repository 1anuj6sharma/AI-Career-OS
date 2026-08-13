from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class RelationshipAgent:
    """
    Agent 2: Relationship Intelligence Agent
    Evaluates relationship strength, connection stage (NEW, CONTACTED, CONNECTED, REFERRAL_DISCUSSION), and interaction recency.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, contact_name: str, previous_interactions_count: int) -> Dict[str, Any]:
        strength = "STRONG" if previous_interactions_count >= 3 else "MODERATE" if previous_interactions_count >= 1 else "WEAK"
        status = "CONNECTED" if previous_interactions_count >= 2 else "CONTACTED" if previous_interactions_count >= 1 else "NEW"

        return {
            "agent": "RelationshipAgent",
            "contact_name": contact_name,
            "relationship_strength": strength,
            "status": status,
            "recommended_outreach_intent": "REFERRAL_REQUEST" if strength == "STRONG" else "RECRUITER_OUTREACH",
        }
