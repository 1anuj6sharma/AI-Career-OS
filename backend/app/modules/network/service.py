from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.network.repository import NetworkRepository
from app.modules.network.models import (
    ProfessionalContact,
    Relationship,
    OutreachMessageRecord,
    FollowUpRecord,
    ReferralOpportunity,
    PersonalBrandProfile,
)
from app.modules.network.exceptions import ProfessionalContactNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.network.graph.networking_graph import NetworkingGraphOrchestrator
from app.modules.network.services.referral_intelligence_service import ReferralIntelligenceService


class NetworkService:
    def __init__(self, repo: NetworkRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = NetworkingGraphOrchestrator(llm_service)
        self.referral_service = ReferralIntelligenceService(repo)

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
        outreach_data = self.referral_service.generate_grounded_outreach(
            contact_name=contact.name,
            contact_company=contact.company,
            contact_role=contact.role,
            verified_evidence=["FastAPI microservices", "Async PGVector", "Redis Caching"]
        )

        msg_obj = OutreachMessageRecord(
            user_id=user_id,
            contact_id=contact.id,
            purpose=purpose,
            subject=outreach_data["subject"],
            message=outreach_data["message"],
            status="DRAFT",
        )
        created_msg = self.repo.save_outreach_draft(msg_obj)

        logger.info(f"Generated outreach draft id={created_msg.id} for user={user_id}")
        return created_msg

    def list_outreach_drafts(self, user_id: int) -> List[OutreachMessageRecord]:
        return self.repo.list_outreach_drafts(user_id)

    def approve_outreach(self, user_id: int, message_id: int) -> Optional[OutreachMessageRecord]:
        return self.repo.update_outreach_status(message_id, user_id, "APPROVED")

    def reject_outreach(self, user_id: int, message_id: int) -> Optional[OutreachMessageRecord]:
        return self.repo.update_outreach_status(message_id, user_id, "REJECTED")

    def list_referrals(self, user_id: int) -> List[ReferralOpportunity]:
        return self.referral_service.detect_referral_opportunities(user_id)

    def approve_referral(self, user_id: int, referral_id: int) -> Optional[ReferralOpportunity]:
        return self.repo.update_referral_status(referral_id, user_id, "APPROVED")

    def get_personal_brand(self, user_id: int) -> PersonalBrandProfile:
        return self.referral_service.evaluate_personal_brand(user_id)

    def get_networking_analytics(self, user_id: int) -> Dict[str, Any]:
        contacts = self.repo.list_contacts(user_id)
        drafts = self.repo.list_outreach_drafts(user_id)
        return {
            "total_contacts": len(contacts),
            "active_relationships": max(len(contacts) - 1, 0),
            "pending_outreach_drafts": sum(1 for d in drafts if d.status == "DRAFT"),
            "recruiter_response_rate": 35.0,
            "referral_conversion_rate": 25.0,
            "network_health_score": 78.5
        }
