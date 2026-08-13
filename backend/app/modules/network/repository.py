from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.network.models import (
    ProfessionalContact,
    Relationship,
    NetworkInteraction,
    OutreachMessageRecord,
    FollowUpRecord,
)


class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

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

    def create_followup(self, followup: FollowUpRecord) -> FollowUpRecord:
        self.db.add(followup)
        self.db.commit()
        self.db.refresh(followup)
        return followup
