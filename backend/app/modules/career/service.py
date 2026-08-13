from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.career.repository import CareerRepository
from app.modules.career.models import CareerRoadmap, CareerMilestone, CareerAdaptation
from app.modules.career.exceptions import CareerRoadmapNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.graph.planner_graph import CareerGraphOrchestrator
from app.modules.career.tools.career_tools import calculate_career_hard_metrics


class CareerService:
    def __init__(self, repo: CareerRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = CareerGraphOrchestrator(llm_service)

    def generate_roadmap(
        self, db: Session, user_id: int, target_role: Optional[str] = None
    ) -> CareerRoadmap:
        # Run closed-loop execution loop
        result = self.graph_orchestrator.run_execution_loop(db, user_id, target_role)

        role = result["target_role"]
        roadmap_data = result["roadmap"]

        # Archive prior active roadmaps
        self.repo.archive_old_roadmaps(user_id)

        # Save new CareerRoadmap
        new_roadmap = CareerRoadmap(
            user_id=user_id,
            target_role=role,
            objective=roadmap_data.get("objective", f"Master skills for {role}"),
            status="ACTIVE",
            version=1,
            roadmap_data=roadmap_data,
        )
        created = self.repo.create_roadmap(new_roadmap)

        # Save Milestones
        for m in roadmap_data.get("milestones", []):
            ms_obj = CareerMilestone(
                roadmap_id=created.id,
                title=m.get("title", "Milestone"),
                description=m.get("description", ""),
                target_date=m.get("target_date", "Month 1"),
                priority="HIGH",
                status="PENDING",
            )
            self.repo.create_milestone(ms_obj)

        logger.info(f"Generated career roadmap id={created.id} version=1 for user={user_id}")
        return self.repo.get_active_roadmap(user_id)

    def get_active_roadmap(self, user_id: int) -> CareerRoadmap:
        roadmap = self.repo.get_active_roadmap(user_id)
        if not roadmap:
            raise CareerRoadmapNotFoundException()
        return roadmap

    def list_roadmaps(self, user_id: int) -> List[CareerRoadmap]:
        return self.repo.list_roadmaps(user_id)

    def get_progress_metrics(self, db: Session, user_id: int) -> Dict[str, Any]:
        return calculate_career_hard_metrics(db, user_id)

    def adapt_active_roadmap(
        self, db: Session, user_id: int, reason: str = "Closed-loop performance adaptation"
    ) -> CareerRoadmap:
        active = self.repo.get_active_roadmap(user_id)
        current_ver = active.version if active else 1
        new_ver_num = current_ver + 1

        result = self.graph_orchestrator.run_execution_loop(db, user_id, active.target_role if active else None)
        role = result["target_role"]
        roadmap_data = result["roadmap"]

        self.repo.archive_old_roadmaps(user_id)

        adapted_roadmap = CareerRoadmap(
            user_id=user_id,
            target_role=role,
            objective=roadmap_data.get("objective", f"Adapted plan v{new_ver_num} for {role}"),
            status="ACTIVE",
            version=new_ver_num,
            roadmap_data=roadmap_data,
        )
        created = self.repo.create_roadmap(adapted_roadmap)

        # Save Adaptation Record
        adapt_rec = CareerAdaptation(
            roadmap_id=created.id,
            version_number=new_ver_num,
            reason=reason,
            adaptation_summary=result.get("adaptation", {}).get("adaptation_reason", "Strategy pivot based on task completion"),
            changes_json=roadmap_data,
        )
        self.repo.create_adaptation(adapt_rec)

        logger.info(f"Adapted career roadmap to version {new_ver_num} for user={user_id}")
        return self.repo.get_active_roadmap(user_id)

    def talk_to_coach(self, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        metrics = calculate_career_hard_metrics(db, user_id)
        active = self.repo.get_active_roadmap(user_id)

        user_context = {
            "target_role": active.target_role if active else "Software Engineer",
            "roadmap_version": active.version if active else 1,
            "metrics": metrics,
        }

        return self.graph_orchestrator.get_coach_response(message, user_context)
