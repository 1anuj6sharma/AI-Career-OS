from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.career.repository import CareerRepository
from app.modules.career.models import (
    CareerRoadmap,
    CareerMilestone,
    CareerAdaptation,
    CareerGoal,
    CareerTask,
    CareerProgress,
    SkillProgress,
    CareerReview,
    CareerRisk,
    CareerScenario,
)
from app.modules.career.exceptions import CareerRoadmapNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.graph.planner_graph import CareerGraphOrchestrator
from app.modules.career.services.performance_service import PerformanceService


class CareerService:
    def __init__(self, repo: CareerRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = CareerGraphOrchestrator(llm_service)
        self.perf_service = PerformanceService(repo)

    # ------------------------------------------------------------------------
    # Roadmap Execution & Adaptation (Module 7 & 13)
    # ------------------------------------------------------------------------
    def generate_roadmap(
        self, db: Session, user_id: int, target_role: Optional[str] = None
    ) -> CareerRoadmap:
        result = self.graph_orchestrator.run_execution_loop(db, user_id, target_role)

        role = result["target_role"]
        roadmap_data = result["roadmap"]

        self.repo.archive_old_roadmaps(user_id)

        new_roadmap = CareerRoadmap(
            user_id=user_id,
            target_role=role,
            objective=roadmap_data.get("objective", f"Master skills for {role}"),
            status="ACTIVE",
            version=1,
            roadmap_data=roadmap_data,
        )
        created = self.repo.create_roadmap(new_roadmap)

        for m in roadmap_data.get("milestones", []):
            ms_obj = CareerMilestone(
                roadmap_id=created.id,
                title=m.get("title", "Milestone"),
                description=m.get("description", ""),
                target_date=m.get("target_date", "Month 1"),
                priority="HIGH",
                status=m.get("status", "PENDING"),
            )
            self.repo.create_milestone(ms_obj)

        logger.info(f"Generated career roadmap id={created.id} version=1 for user={user_id}")
        return self.repo.get_active_roadmap(user_id)

    def get_active_roadmap(self, user_id: int) -> CareerRoadmap:
        roadmap = self.repo.get_active_roadmap(user_id)
        if not roadmap:
            # Auto-generate baseline roadmap if none exists
            return None
        return roadmap

    def list_roadmaps(self, user_id: int) -> List[CareerRoadmap]:
        return self.repo.list_roadmaps(user_id)

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

        adapt_rec = CareerAdaptation(
            roadmap_id=created.id,
            version_number=new_ver_num,
            reason=reason,
            adaptation_summary=f"Strategy pivot based on performance data: {reason}",
            changes_json=roadmap_data,
        )
        self.repo.create_adaptation(adapt_rec)

        logger.info(f"Adapted career roadmap to version {new_ver_num} for user={user_id}")
        return self.repo.get_active_roadmap(user_id)

    # ------------------------------------------------------------------------
    # Module 13 Goals Management
    # ------------------------------------------------------------------------
    def create_goal(self, user_id: int, data: Any) -> CareerGoal:
        goal = CareerGoal(
            user_id=user_id,
            title=data.title,
            description=data.description,
            goal_type=data.goal_type,
            priority=data.priority,
            status="ACTIVE",
            target_date=data.target_date,
        )
        return self.repo.create_goal(goal)

    def list_goals(self, user_id: int, status: Optional[str] = None) -> List[CareerGoal]:
        return self.repo.list_goals(user_id, status)

    def update_goal_status(self, goal_id: int, user_id: int, new_status: str) -> Optional[CareerGoal]:
        return self.repo.update_goal_status(goal_id, user_id, new_status)

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        return self.repo.delete_goal(goal_id, user_id)

    # ------------------------------------------------------------------------
    # Module 13 Tasks Management
    # ------------------------------------------------------------------------
    def create_task(self, user_id: int, data: Any) -> CareerTask:
        task = CareerTask(
            user_id=user_id,
            milestone_id=data.milestone_id,
            goal_id=data.goal_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status="PENDING",
            estimated_minutes=data.estimated_minutes,
            due_date=data.due_date,
        )
        return self.repo.create_task(task)

    def list_tasks(self, user_id: int, status: Optional[str] = None) -> List[CareerTask]:
        return self.repo.list_tasks(user_id, status)

    def update_task_status(self, task_id: int, user_id: int, status: str) -> Optional[CareerTask]:
        return self.repo.update_task_status(task_id, user_id, status)

    # ------------------------------------------------------------------------
    # Module 13 Performance, Readiness & Dashboard
    # ------------------------------------------------------------------------
    def get_performance_dashboard(self, db: Session, user_id: int) -> Dict[str, Any]:
        perf_data = self.perf_service.calculate_performance_score(db, user_id)
        readiness = self.perf_service.calculate_career_readiness(db, user_id)
        goals = self.repo.list_goals(user_id)
        tasks = self.repo.list_tasks(user_id)
        skills = self.repo.list_skill_progress(user_id)
        risks = self.repo.list_active_risks(user_id)
        latest_review = self.repo.get_latest_review(user_id)
        roadmap = self.repo.get_active_roadmap(user_id)

        completed_t = [t for t in tasks if t.status == "COMPLETED"]
        pending_t = [t for t in tasks if t.status == "PENDING"]

        return {
            "user_id": user_id,
            "target_role": readiness["target_role"],
            "overall_readiness_score": readiness["overall_readiness"],
            "performance_score": perf_data["performance_score"],
            "performance_breakdown": perf_data["breakdown"],
            "active_goals_count": len([g for g in goals if g.status == "ACTIVE"]),
            "pending_tasks_count": len(pending_t),
            "completed_tasks_count": len(completed_t),
            "skills_summary": skills,
            "active_risks": risks,
            "recent_review": latest_review,
            "roadmap_version": roadmap.version if roadmap else 1
        }

    # ------------------------------------------------------------------------
    # Module 13 Skill Progress, Reviews, Risks & Scenarios
    # ------------------------------------------------------------------------
    def list_skill_progress(self, user_id: int) -> List[SkillProgress]:
        return self.repo.list_skill_progress(user_id)

    def generate_review(self, db: Session, user_id: int, review_type: str = "WEEKLY") -> CareerReview:
        perf_data = self.perf_service.calculate_performance_score(db, user_id)
        review_agent = self.graph_orchestrator.review_agent
        agent_out = review_agent.run({"review_type": review_type, "performance_score": perf_data["performance_score"]})

        review = CareerReview(
            user_id=user_id,
            review_type=review_type,
            period_start=datetime.now(),
            period_end=datetime.now(),
            performance_score=agent_out.performance_score,
            summary=agent_out.summary,
            strengths=agent_out.completed_highlights,
            weaknesses=agent_out.missed_goals,
            recommendations=agent_out.next_period_priorities,
        )
        return self.repo.create_review(review)

    def list_reviews(self, user_id: int) -> List[CareerReview]:
        return self.repo.list_reviews(user_id)

    def list_active_risks(self, user_id: int) -> List[CareerRisk]:
        return self.repo.list_active_risks(user_id)

    def simulate_scenario(self, user_id: int, scenario_name: str, target_role: str, assumptions: Optional[Dict[str, Any]] = None) -> CareerScenario:
        scenario_agent = self.graph_orchestrator.scenario_agent
        sim_output = scenario_agent.run("Software Engineer", target_role, assumptions or {})

        scenario = CareerScenario(
            user_id=user_id,
            scenario_name=scenario_name,
            target_role=target_role,
            assumptions=assumptions,
            projection=sim_output.dict(),
        )
        return self.repo.create_scenario(scenario)

    def list_scenarios(self, user_id: int) -> List[CareerScenario]:
        return self.repo.list_scenarios(user_id)

    def talk_to_coach(self, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        dashboard = self.get_performance_dashboard(db, user_id)
        user_context = {
            "target_role": dashboard["target_role"],
            "performance_score": dashboard["performance_score"],
            "readiness": dashboard["overall_readiness_score"],
            "roadmap_version": dashboard["roadmap_version"],
        }
        return self.graph_orchestrator.get_coach_response(message, user_context)
