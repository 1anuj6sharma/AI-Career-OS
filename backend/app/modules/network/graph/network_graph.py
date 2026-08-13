from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.network.agents import (
    NetworkDiscoveryAgent,
    RelationshipAgent,
    OutreachAgent,
    ConversationAgent,
    FollowupAgent,
    NetworkingCoachAgent,
    OpportunityNetworkAgent,
)


class NetworkGraphOrchestrator:
    """
    Module 11 LangGraph Stateful Workflow Engine.
    Orchestrates recruiter discovery, relationship evaluation, personalized outreach drafting (requiring human approval), conversation analysis, and follow-up scheduling.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.discovery_agent = NetworkDiscoveryAgent(llm_service)
        self.relationship_agent = RelationshipAgent(llm_service)
        self.outreach_agent = OutreachAgent(llm_service)
        self.conversation_agent = ConversationAgent(llm_service)
        self.followup_agent = FollowupAgent(llm_service)
        self.coach_agent = NetworkingCoachAgent(llm_service)
        self.opportunity_agent = OpportunityNetworkAgent(llm_service)

    def run_outreach_pipeline(
        self, user_id: int, contact_name: str, contact_role: str, company_name: str, purpose: str = "RECRUITER_OUTREACH"
    ) -> Dict[str, Any]:
        # 1. Evaluate relationship stage
        rel_info = self.relationship_agent.run(contact_name, previous_interactions_count=0)

        # 2. Draft personalized outreach message grounded in RAG evidence
        draft = self.outreach_agent.run(
            user_id=user_id,
            contact_name=contact_name,
            contact_role=contact_role,
            company_name=company_name,
            purpose=purpose,
        )

        # 3. Calculate follow-up reminder date
        followup_info = self.followup_agent.run(contact_name, purpose)

        return {
            "relationship_evaluation": rel_info,
            "outreach_draft": draft,
            "approval_status": "DRAFT",  # Mandatory human-in-the-loop gate
            "follow_up_info": followup_info,
        }

    def analyze_recruiter_conversation(self, message_text: str) -> Dict[str, Any]:
        return self.conversation_agent.run(message_text)

    def talk_to_coach(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        return self.coach_agent.run(message, user_context)
