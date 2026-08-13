from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.learning.repository import LearningRepository
from app.modules.learning.models import (
    LearningPath,
    LearningModule,
    LearningTopic,
    LearningResource,
    LearningAssessment,
)
from app.modules.learning.exceptions import LearningPathNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.learning.graph.learning_graph import LearningGraphOrchestrator
from app.modules.career.models import CareerRoadmap


class LearningService:
    def __init__(self, repo: LearningRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = LearningGraphOrchestrator(llm_service)

    def generate_learning_path(
        self, db: Session, user_id: int, target_role: Optional[str] = None
    ) -> LearningPath:
        # Fetch active career roadmap or default role
        active_roadmap = db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE").first()
        role = target_role or (active_roadmap.target_role if active_roadmap else "Backend Engineer")

        high_priority_gaps = ["Docker & Containerization", "PostgreSQL Query Tuning", "System Design Caching"]

        # Run pipeline
        path_plan = self.graph_orchestrator.generate_learning_path_pipeline(role, high_priority_gaps)

        # Archive old active paths
        self.repo.archive_old_paths(user_id)

        # Save LearningPath
        new_path = LearningPath(
            user_id=user_id,
            title=path_plan.get("title", f"Personalized Learning Path for {role}"),
            description=path_plan.get("description", "Curriculum derived from Module 7 skill gaps"),
            status="ACTIVE",
        )
        created_path = self.repo.create_path(new_path)

        # Save Modules, Topics, and Resources
        for mod in path_plan.get("modules", []):
            mod_obj = LearningModule(
                learning_path_id=created_path.id,
                title=mod.get("title", "Module"),
                description=mod.get("description", ""),
                sequence=mod.get("sequence", 1),
            )
            created_mod = self.repo.create_module(mod_obj)

            for top in mod.get("topics", []):
                top_obj = LearningTopic(
                    module_id=created_mod.id,
                    title=top.get("title", "Topic"),
                    difficulty=top.get("difficulty", "INTERMEDIATE"),
                    estimated_minutes=top.get("estimated_minutes", 30),
                    status="PENDING",
                )
                created_top = self.repo.create_topic(top_obj)

                for res in top.get("resources", []):
                    res_obj = LearningResource(
                        topic_id=created_top.id,
                        title=res.get("title", "Resource"),
                        resource_type=res.get("resource_type", "DOCUMENTATION"),
                        url=res.get("url"),
                        difficulty=res.get("difficulty", "INTERMEDIATE"),
                        relevance_score=res.get("relevance_score", 90.0),
                    )
                    self.repo.create_resource(res_obj)

        logger.info(f"Generated learning path id={created_path.id} for user={user_id}")
        return self.repo.get_active_path(user_id)

    def get_active_path(self, user_id: int) -> LearningPath:
        path = self.repo.get_active_path(user_id)
        if not path:
            raise LearningPathNotFoundException()
        return path

    def list_paths(self, user_id: int) -> List[LearningPath]:
        return self.repo.list_paths(user_id)

    def query_tutor(self, topic: str, question: str, mode: str = "INTERMEDIATE") -> Dict[str, Any]:
        return self.graph_orchestrator.tutor_query_pipeline(topic, question, mode)

    def generate_practice(self, topic: str) -> Dict[str, Any]:
        return self.graph_orchestrator.generate_practice_pipeline(topic)

    def assess_submission(
        self, db: Session, user_id: int, topic_id: Optional[int], topic_title: str, submission_text: str
    ) -> LearningAssessment:
        result = self.graph_orchestrator.assess_submission_pipeline(db, user_id, topic_title, submission_text)

        assessment = LearningAssessment(
            user_id=user_id,
            topic_id=topic_id,
            score=result.get("score", 85.0),
            feedback=result.get("feedback", ""),
        )
        created = self.repo.create_assessment(assessment)
        return created
