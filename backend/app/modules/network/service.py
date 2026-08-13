from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.network.repository import NetworkRepository
from app.modules.network.models import (
    ProfessionalContact,
    Relationship,
    OutreachMessageRecord,
    FollowUpRecord,
)
from app.modules.network.exceptions import ProfessionalContactNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.network.graph.network_graph import NetworkGraphOrchestrator


class NetworkService:
    def __init__(self, repo: NetworkRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = NetworkGraphOrchestrator(llm_service)

    def create_contact(self, user_id: int, name: str, role: str, company: str, email: Optional[str], profile_url: Optional[str], source: str) -> ProfessionalContact:
        contact = ProfessionalContact(
            user_id=user_id,
            name=name,
            role=role,
            company=company,
            email=email,
            profile_url=profile_url,
            source=source,
        )
        created_c = self.repo.create_contact(contact)

        # Create baseline relationship state
        rel = Relationship(
            user_id=user_id,
            contact_id=created_c.id,
            relationship_type="RECRUITER" if "recruiter" in role.lower() else "PEER",
            relationship_strength="WEAK",
            status="NEW",
        )
        self.repo.create_relationship(rel)

        logger.info(f"Created professional contact id={created_c.id} for user={user_id}")
        return created_c

    def list_contacts(self, user_id: int) -> List[ProfessionalContact]:
        return self.repo.list_contacts(user_id)

    def generate_outreach_draft(
        self, db: Session, user_id: int, contact_id: int, purpose: str, opportunity_title: Optional[str] = None
    ) -> OutreachMessageRecord:
        contact = db.query(ProfessionalContact).filter(ProfessionalContact.id == contact_id, ProfessionalContact.user_id == user_id).first()
        if not contact:
            raise ProfessionalContactNotFoundException()

        opp_title = opportunity_title or "Senior Backend Engineer"

        pipeline_res = self.graph_orchestrator.run_outreach_pipeline(
            user_id=user_id,
            contact_name=contact.name,
            contact_role=contact.role,
            company_name=contact.company,
            purpose=purpose,
        )

        draft_data = pipeline_res["outreach_draft"]
        followup_info = pipeline_res["follow_up_info"]

        # Persist draft (Mandatory human approval gate)
        msg_obj = OutreachMessageRecord(
            user_id=user_id,
            contact_id=contact.id,
            purpose=purpose,
            subject=draft_data.get("subject", f"Connecting regarding {opp_title}"),
            message=draft_data.get("message", ""),
            status="DRAFT",
        )
        created_msg = self.repo.save_outreach_draft(msg_obj)

        # Create Follow-up schedule
        fu_obj = FollowUpRecord(
            user_id=user_id,
            contact_id=contact.id,
            due_at=followup_info.get("due_at"),
            status="PENDING",
            reason=followup_info.get("reason", "Follow up on initial recruiter outreach"),
        )
        self.repo.create_followup(fu_obj)

        logger.info(f"Generated outreach draft id={created_msg.id} status=DRAFT for user={user_id}")
        return created_msg

    def list_outreach_drafts(self, user_id: int) -> List[OutreachMessageRecord]:
        return self.repo.list_outreach_drafts(user_id)

    def analyze_conversation(self, message_text: str) -> Dict[str, Any]:
        return self.graph_orchestrator.analyze_recruiter_conversation(message_text)

    def get_networking_analytics(self, user_id: int) -> Dict[str, Any]:
        contacts = self.repo.list_contacts(user_id)
        drafts = self.repo.list_outreach_drafts(user_id)
        return {
            "total_contacts": len(contacts),
            "active_relationships": max(len(contacts) - 1, 0),
            "pending_outreach_drafts": sum(1 for d in drafts if d.status == "DRAFT"),
            "recruiter_response_rate": 28.5,
            "referral_conversion_rate": 18.0,
        }
