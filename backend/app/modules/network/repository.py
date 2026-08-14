from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.network.models import (
    ProfessionalContact,
    Relationship,
    NetworkInteraction,
    OutreachMessageRecord,
    FollowUpRecord,
    ReferralOpportunity,
    PersonalBrandProfile,
    ContentIdeaRecord,
    NetworkAnalyticsRecord,
)


class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------------
    # Contacts & Relationships
    # ------------------------------------------------------------------------
    def create_contact(self, contact: ProfessionalContact) -> ProfessionalContact:
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def list_contacts(self, user_id: int) -> List[ProfessionalContact]:
        return (
            self.db.query(ProfessionalContact)
            .filter(ProfessionalContact.user_id == user_id)
            .order_by(ProfessionalContact.created_at.desc())
            .all()
        )

    def create_relationship(self, rel: Relationship) -> Relationship:
        self.db.add(rel)
        self.db.commit()
        self.db.refresh(rel)
        return rel

    # ------------------------------------------------------------------------
    # Outreach Messages
    # ------------------------------------------------------------------------
    def save_outreach_draft(self, msg: OutreachMessageRecord) -> OutreachMessageRecord:
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_outreach_drafts(self, user_id: int) -> List[OutreachMessageRecord]:
        return (
            self.db.query(OutreachMessageRecord)
            .options(joinedload(OutreachMessageRecord.contact))
            .filter(OutreachMessageRecord.user_id == user_id)
            .order_by(OutreachMessageRecord.created_at.desc())
            .all()
        )

    def update_outreach_status(self, message_id: int, user_id: int, status: str) -> Optional[OutreachMessageRecord]:
        msg = (
            self.db.query(OutreachMessageRecord)
            .filter(OutreachMessageRecord.id == message_id, OutreachMessageRecord.user_id == user_id)
            .first()
        )
        if msg:
            msg.status = status
            self.db.commit()
            self.db.refresh(msg)
        return msg

    # ------------------------------------------------------------------------
    # Follow Ups
    # ------------------------------------------------------------------------
    def create_followup(self, followup: FollowUpRecord) -> FollowUpRecord:
        self.db.add(followup)
        self.db.commit()
        self.db.refresh(followup)
        return followup

    def list_followups(self, user_id: int) -> List[FollowUpRecord]:
        return (
            self.db.query(FollowUpRecord)
            .filter(FollowUpRecord.user_id == user_id)
            .order_by(FollowUpRecord.due_at.asc())
            .all()
        )

    # ------------------------------------------------------------------------
    # Module 16 — Referral Opportunities
    # ------------------------------------------------------------------------
    def create_referral_opportunity(self, ref: ReferralOpportunity) -> ReferralOpportunity:
        self.db.add(ref)
        self.db.commit()
        self.db.refresh(ref)
        return ref

    def list_referral_opportunities(self, user_id: int) -> List[ReferralOpportunity]:
        return (
            self.db.query(ReferralOpportunity)
            .options(joinedload(ReferralOpportunity.contact), joinedload(ReferralOpportunity.opportunity))
            .filter(ReferralOpportunity.user_id == user_id)
            .order_by(ReferralOpportunity.referral_score.desc())
            .all()
        )

    def update_referral_status(self, referral_id: int, user_id: int, status: str) -> Optional[ReferralOpportunity]:
        ref = (
            self.db.query(ReferralOpportunity)
            .filter(ReferralOpportunity.id == referral_id, ReferralOpportunity.user_id == user_id)
            .first()
        )
        if ref:
            ref.status = status
            self.db.commit()
            self.db.refresh(ref)
        return ref

    # ------------------------------------------------------------------------
    # Module 16 — Personal Brand & Content
    # ------------------------------------------------------------------------
    def get_personal_brand_profile(self, user_id: int) -> Optional[PersonalBrandProfile]:
        return (
            self.db.query(PersonalBrandProfile)
            .filter(PersonalBrandProfile.user_id == user_id)
            .order_by(PersonalBrandProfile.updated_at.desc())
            .first()
        )

    def create_personal_brand_profile(self, brand: PersonalBrandProfile) -> PersonalBrandProfile:
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def create_content_idea(self, idea: ContentIdeaRecord) -> ContentIdeaRecord:
        self.db.add(idea)
        self.db.commit()
        self.db.refresh(idea)
        return idea
