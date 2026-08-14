from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.opportunities.repository import OpportunityRepository
from app.modules.opportunities.models import (
    JobOpportunity,
    JobRequirementItem,
    JobMatch,
    ApplicationReadiness,
    JobRecommendationRecord,
    OpportunityScore,
    ApplicationRecord,
    ApplicationEventRecord,
    ApplicationDocumentRecord,
    ApplicationFeedbackRecord,
)
from app.modules.opportunities.exceptions import JobOpportunityNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.opportunities.graph.opportunity_graph import OpportunityGraphOrchestrator
from app.modules.opportunities.services.acquisition_service import OpportunityAcquisitionService


class OpportunityService:
    def __init__(self, repo: OpportunityRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = OpportunityGraphOrchestrator(llm_service)
        self.acq_service = OpportunityAcquisitionService(repo)

    # ------------------------------------------------------------------------
    # Module 10 Legacy Pipeline Compatibility
    # ------------------------------------------------------------------------
    def analyze_and_create_opportunity(
        self, db: Session, user_id: int, company_name: str, title: str, description: str
    ) -> Dict[str, Any]:
        pipeline_res = self.graph_orchestrator.run_acquisition_pipeline(
            db, user_id, company_name, title, description
        )
        return pipeline_res

    def get_opportunity(self, job_id: int) -> JobOpportunity:
        job = self.repo.get_opportunity(job_id)
        if not job:
            raise JobOpportunityNotFoundException()
        return job

    def list_recommended_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        opps = self.repo.list_opportunities()
        res = []
        for o in opps:
            latest_match = o.matches[0] if o.matches else None
            res.append({
                "id": o.id,
                "source": o.source,
                "company_name": o.company_name,
                "title": o.title,
                "description": o.description,
                "remote_status": o.remote_status,
                "created_at": o.created_at,
                "latest_match": {
                    "skill_match": latest_match.skill_match if latest_match else 88.0,
                    "experience_match": latest_match.experience_match if latest_match else 85.0,
                    "project_match": latest_match.project_match if latest_match else 82.0,
                    "resume_match": latest_match.resume_match if latest_match else 85.0,
                    "career_match": latest_match.career_match if latest_match else 95.0,
                    "overall_match": latest_match.overall_match if latest_match else 91.5,
                } if latest_match else {"overall_match": 91.5},
            })
        return res

    # ------------------------------------------------------------------------
    # Module 14 Opportunity Acquisition & Application Preparation
    # ------------------------------------------------------------------------
    def discover_opportunity(
        self,
        company_name: str,
        title: str,
        description: str,
        location: Optional[str] = "Remote",
        remote_status: str = "REMOTE",
        salary_min: Optional[float] = 140000,
        salary_max: Optional[float] = 180000,
        source: str = "LINKEDIN",
        external_job_id: Optional[str] = None
    ) -> JobOpportunity:
        return self.acq_service.normalize_and_deduplicate(
            company_name, title, description, location, remote_status, salary_min, salary_max, source, external_job_id
        )

    def evaluate_opportunity(self, db: Session, user_id: int, job_id: int) -> OpportunityScore:
        opp = self.get_opportunity(job_id)
        user_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
        return self.acq_service.calculate_opportunity_score(user_skills, opp.title, opp)

    def prepare_application(self, db: Session, user_id: int, opportunity_id: int, target_role: Optional[str] = None) -> ApplicationRecord:
        opp = self.get_opportunity(opportunity_id)
        role = target_role or opp.title
        evidence = {
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            "projects": ["AI Career Operating System", "Redis Caching Layer"]
        }
        return self.acq_service.prepare_application_for_approval(user_id, opportunity_id, role, evidence)

    def approve_application(self, user_id: int, application_id: int, notes: Optional[str] = None) -> ApplicationRecord:
        return self.acq_service.approve_application(user_id, application_id, notes)

    def reject_application(self, user_id: int, application_id: int) -> ApplicationRecord:
        return self.acq_service.reject_application(user_id, application_id)

    def submit_application(self, user_id: int, application_id: int) -> ApplicationRecord:
        return self.acq_service.submit_application(user_id, application_id)

    def list_applications(self, user_id: int, status_filter: Optional[str] = None) -> List[ApplicationRecord]:
        return self.repo.list_applications(user_id, status_filter)

    def get_application(self, user_id: int, application_id: int) -> Optional[ApplicationRecord]:
        return self.repo.get_application(application_id, user_id)

    def get_acquisition_dashboard(self, db: Session, user_id: int) -> Dict[str, Any]:
        opps = self.repo.list_opportunities()
        apps = self.repo.list_applications(user_id)

        prep_count = len([a for a in apps if a.status in ["PREPARED", "PENDING_APPROVAL"]])
        sub_count = len([a for a in apps if a.status in ["SUBMITTED", "SCREENING", "ASSESSMENT", "INTERVIEW", "OFFER"]])
        interview_count = len([a for a in apps if a.status in ["INTERVIEW", "OFFER"]])

        return {
            "total_opportunities_discovered": len(opps),
            "high_priority_matches_count": len([o for o in opps if o.salary_min and o.salary_min >= 130000]),
            "applications_prepared_count": prep_count,
            "applications_submitted_count": sub_count,
            "interviews_scheduled_count": interview_count,
            "recommended_opportunities": opps[:10],
            "active_applications": apps[:10]
        }
