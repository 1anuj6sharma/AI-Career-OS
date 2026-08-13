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
)
from app.modules.opportunities.exceptions import JobOpportunityNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.opportunities.graph.opportunity_graph import OpportunityGraphOrchestrator


class OpportunityService:
    def __init__(self, repo: OpportunityRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = OpportunityGraphOrchestrator(llm_service)

    def analyze_and_create_opportunity(
        self, db: Session, user_id: int, company_name: str, title: str, description: str
    ) -> Dict[str, Any]:
        # Run stateful pipeline
        pipeline_res = self.graph_orchestrator.run_opportunity_pipeline(
            db, user_id, description, title, company_name
        )

        parsed = pipeline_res["parsed_job"]
        match_breakdown = pipeline_res["match_breakdown"]
        readiness_info = pipeline_res["readiness"]

        # Create JobOpportunity in DB
        job_obj = JobOpportunity(
            company_name=company_name,
            title=title,
            description=description,
            source="USER_IMPORTED",
            remote_status="HYBRID",
        )
        created_job = self.repo.create_opportunity(job_obj)

        # Save Requirements
        for req_skill in parsed.get("required_skills", []):
            req_item = JobRequirementItem(
                job_id=created_job.id,
                skill=req_skill,
                requirement_type="REQUIRED",
                importance=1.0,
            )
            self.repo.create_requirement(req_item)

        for pref_skill in parsed.get("preferred_skills", []):
            req_item = JobRequirementItem(
                job_id=created_job.id,
                skill=pref_skill,
                requirement_type="PREFERRED",
                importance=0.6,
            )
            self.repo.create_requirement(req_item)

        # Save JobMatch
        match_obj = JobMatch(
            user_id=user_id,
            job_id=created_job.id,
            skill_match=match_breakdown["skill_match"],
            experience_match=match_breakdown["experience_match"],
            project_match=match_breakdown["project_match"],
            resume_match=match_breakdown["resume_match"],
            career_match=match_breakdown["career_match"],
            overall_match=match_breakdown["overall_match"],
        )
        self.repo.save_match(match_obj)

        # Save ApplicationReadiness
        readiness_obj = ApplicationReadiness(
            user_id=user_id,
            job_id=created_job.id,
            readiness_score=readiness_info["readiness_score"],
            resume_score=match_breakdown["resume_match"],
            skill_score=match_breakdown["skill_match"],
            project_score=match_breakdown["project_match"],
            interview_score=80.0,
        )
        self.repo.save_readiness(readiness_obj)

        # Save JobRecommendationRecord
        rec_obj = JobRecommendationRecord(
            user_id=user_id,
            job_id=created_job.id,
            recommendation=readiness_info["recommendation"],
            priority=readiness_info["priority"],
            reason=readiness_info["reason"],
            estimated_preparation_hours=readiness_info["estimated_preparation_hours"],
        )
        self.repo.save_recommendation(rec_obj)

        pipeline_res["job_id"] = created_job.id
        logger.info(f"Analyzed & created opportunity id={created_job.id} match={match_breakdown['overall_match']}% for user={user_id}")
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
                    "skill_match": latest_match.skill_match if latest_match else 0.0,
                    "experience_match": latest_match.experience_match if latest_match else 0.0,
                    "project_match": latest_match.project_match if latest_match else 0.0,
                    "resume_match": latest_match.resume_match if latest_match else 0.0,
                    "career_match": latest_match.career_match if latest_match else 0.0,
                    "overall_match": latest_match.overall_match if latest_match else 85.0,
                } if latest_match else {"overall_match": 85.0},
            })
        return res
