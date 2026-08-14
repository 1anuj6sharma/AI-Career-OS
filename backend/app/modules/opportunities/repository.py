from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.modules.opportunities.models import (
    JobOpportunity,
    JobRequirementItem,
    JobMatch,
    ApplicationReadiness,
    JobRecommendationRecord,
    CompanyIntelligenceRecord,
    OpportunityScore,
    ApplicationStrategyRecord,
    ApplicationRecord,
    ApplicationEventRecord,
    ApplicationDocumentRecord,
    ApplicationFeedbackRecord,
)


class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------------
    # Base Opportunities
    # ------------------------------------------------------------------------
    def create_opportunity(self, job: JobOpportunity) -> JobOpportunity:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def find_existing_opportunity(
        self, company_name: str, title: str, external_job_id: Optional[str] = None
    ) -> Optional[JobOpportunity]:
        if external_job_id:
            existing = (
                self.db.query(JobOpportunity)
                .filter(JobOpportunity.external_job_id == external_job_id)
                .first()
            )
            if existing:
                return existing

        return (
            self.db.query(JobOpportunity)
            .filter(
                JobOpportunity.company_name.ilike(f"%{company_name}%"),
                JobOpportunity.title.ilike(f"%{title}%"),
            )
            .first()
        )

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

    # ------------------------------------------------------------------------
    # Module 14 Opportunity Scoring & Strategy
    # ------------------------------------------------------------------------
    def save_opportunity_score(self, score: OpportunityScore) -> OpportunityScore:
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def get_opportunity_score(self, opportunity_id: int) -> Optional[OpportunityScore]:
        return (
            self.db.query(OpportunityScore)
            .filter(OpportunityScore.opportunity_id == opportunity_id)
            .order_by(OpportunityScore.created_at.desc())
            .first()
        )

    def save_application_strategy(self, strategy: ApplicationStrategyRecord) -> ApplicationStrategyRecord:
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def get_application_strategy(self, user_id: int, opportunity_id: int) -> Optional[ApplicationStrategyRecord]:
        return (
            self.db.query(ApplicationStrategyRecord)
            .filter(
                ApplicationStrategyRecord.user_id == user_id,
                ApplicationStrategyRecord.opportunity_id == opportunity_id,
            )
            .order_by(ApplicationStrategyRecord.created_at.desc())
            .first()
        )

    # ------------------------------------------------------------------------
    # Module 14 Applications & Tracking
    # ------------------------------------------------------------------------
    def create_application(self, application: ApplicationRecord) -> ApplicationRecord:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application(self, application_id: int, user_id: int) -> Optional[ApplicationRecord]:
        return (
            self.db.query(ApplicationRecord)
            .options(
                joinedload(ApplicationRecord.opportunity),
                joinedload(ApplicationRecord.events),
                joinedload(ApplicationRecord.documents),
            )
            .filter(ApplicationRecord.id == application_id, ApplicationRecord.user_id == user_id)
            .first()
        )

    def list_applications(self, user_id: int, status: Optional[str] = None) -> List[ApplicationRecord]:
        query = (
            self.db.query(ApplicationRecord)
            .options(
                joinedload(ApplicationRecord.opportunity),
                joinedload(ApplicationRecord.events),
                joinedload(ApplicationRecord.documents),
            )
            .filter(ApplicationRecord.user_id == user_id)
        )
        if status:
            query = query.filter(ApplicationRecord.status == status)
        return query.order_by(ApplicationRecord.updated_at.desc()).all()

    def update_application_status(
        self, application_id: int, user_id: int, new_status: str
    ) -> Optional[ApplicationRecord]:
        app = self.get_application(application_id, user_id)
        if app:
            app.status = new_status
            if new_status == "SUBMITTED":
                app.applied_at = datetime.now()
            self.db.commit()
            self.db.refresh(app)
        return app

    def add_application_event(self, event: ApplicationEventRecord) -> ApplicationEventRecord:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def add_application_document(self, doc: ApplicationDocumentRecord) -> ApplicationDocumentRecord:
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    # ------------------------------------------------------------------------
    # Module 14 Feedback Learning
    # ------------------------------------------------------------------------
    def save_feedback(self, feedback: ApplicationFeedbackRecord) -> ApplicationFeedbackRecord:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_latest_feedback(self, user_id: int) -> Optional[ApplicationFeedbackRecord]:
        return (
            self.db.query(ApplicationFeedbackRecord)
            .filter(ApplicationFeedbackRecord.user_id == user_id)
            .order_by(ApplicationFeedbackRecord.created_at.desc())
            .first()
        )
