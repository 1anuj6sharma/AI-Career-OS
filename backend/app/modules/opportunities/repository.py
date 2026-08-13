from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.opportunities.models import (
    JobOpportunity,
    JobRequirementItem,
    JobMatch,
    ApplicationReadiness,
    JobRecommendationRecord,
    CompanyIntelligenceRecord,
)


class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_opportunity(self, job: JobOpportunity) -> JobOpportunity:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_opportunity(self, job_id: int) -> Optional[JobOpportunity]:
        return (
            self.db.query(JobOpportunity)
            .options(
                joinedload(JobOpportunity.requirements),
                joinedload(JobOpportunity.matches),
            )
            .filter(JobOpportunity.id == job_id)
            .first()
        )

    def list_opportunities(self) -> List[JobOpportunity]:
        return (
            self.db.query(JobOpportunity)
            .options(joinedload(JobOpportunity.matches))
            .order_by(JobOpportunity.created_at.desc())
            .all()
        )

    def create_requirement(self, req: JobRequirementItem) -> JobRequirementItem:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def save_match(self, match: JobMatch) -> JobMatch:
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def save_readiness(self, readiness: ApplicationReadiness) -> ApplicationReadiness:
        self.db.add(readiness)
        self.db.commit()
        self.db.refresh(readiness)
        return readiness

    def save_recommendation(self, rec: JobRecommendationRecord) -> JobRecommendationRecord:
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec
