from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
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


class CareerRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------------
    # Roadmaps & Milestones
    # ------------------------------------------------------------------------
    def create_roadmap(self, roadmap: CareerRoadmap) -> CareerRoadmap:
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def get_active_roadmap(self, user_id: int) -> Optional[CareerRoadmap]:
        return (
            self.db.query(CareerRoadmap)
            .options(
                joinedload(CareerRoadmap.milestones),
                joinedload(CareerRoadmap.adaptations),
            )
            .filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE")
            .order_by(CareerRoadmap.version.desc())
            .first()
        )

    def list_roadmaps(self, user_id: int) -> List[CareerRoadmap]:
        return (
            self.db.query(CareerRoadmap)
            .options(
                joinedload(CareerRoadmap.milestones),
                joinedload(CareerRoadmap.adaptations),
            )
            .filter(CareerRoadmap.user_id == user_id)
            .order_by(CareerRoadmap.created_at.desc())
            .all()
        )

    def create_milestone(self, milestone: CareerMilestone) -> CareerMilestone:
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def create_adaptation(self, adaptation: CareerAdaptation) -> CareerAdaptation:
        self.db.add(adaptation)
        self.db.commit()
        self.db.refresh(adaptation)
        return adaptation

    def archive_old_roadmaps(self, user_id: int) -> None:
        self.db.query(CareerRoadmap).filter(
            CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE"
        ).update({"status": "ADAPTED"})
        self.db.commit()

    # ------------------------------------------------------------------------
    # Career Goals
    # ------------------------------------------------------------------------
    def create_goal(self, goal: CareerGoal) -> CareerGoal:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def get_goal(self, goal_id: int, user_id: int) -> Optional[CareerGoal]:
        return (
            self.db.query(CareerGoal)
            .filter(CareerGoal.id == goal_id, CareerGoal.user_id == user_id)
            .first()
        )

    def list_goals(self, user_id: int, status: Optional[str] = None) -> List[CareerGoal]:
        query = self.db.query(CareerGoal).filter(CareerGoal.user_id == user_id)
        if status:
            query = query.filter(CareerGoal.status == status)
        return query.order_by(CareerGoal.priority.asc(), CareerGoal.created_at.desc()).all()

    def update_goal_status(self, goal_id: int, user_id: int, new_status: str) -> Optional[CareerGoal]:
        goal = self.get_goal(goal_id, user_id)
        if goal:
            goal.status = new_status
            self.db.commit()
            self.db.refresh(goal)
        return goal

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        goal = self.get_goal(goal_id, user_id)
        if goal:
            self.db.delete(goal)
            self.db.commit()
            return True
        return False

    # ------------------------------------------------------------------------
    # Career Tasks
    # ------------------------------------------------------------------------
    def create_task(self, task: CareerTask) -> CareerTask:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: int, user_id: int) -> Optional[CareerTask]:
        return (
            self.db.query(CareerTask)
            .filter(CareerTask.id == task_id, CareerTask.user_id == user_id)
            .first()
        )

    def list_tasks(self, user_id: int, status: Optional[str] = None) -> List[CareerTask]:
        query = self.db.query(CareerTask).filter(CareerTask.user_id == user_id)
        if status:
            query = query.filter(CareerTask.status == status)
        return query.order_by(CareerTask.created_at.desc()).all()

    def update_task_status(self, task_id: int, user_id: int, status: str) -> Optional[CareerTask]:
        task = self.get_task(task_id, user_id)
        if task:
            task.status = status
            if status == "COMPLETED":
                task.completed_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
        return task

    # ------------------------------------------------------------------------
    # Career Progress Records
    # ------------------------------------------------------------------------
    def create_progress_record(self, progress: CareerProgress) -> CareerProgress:
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_latest_progress(self, user_id: int) -> List[CareerProgress]:
        return (
            self.db.query(CareerProgress)
            .filter(CareerProgress.user_id == user_id)
            .order_by(CareerProgress.recorded_at.desc())
            .limit(20)
            .all()
        )

    # ------------------------------------------------------------------------
    # Skill Progress
    # ------------------------------------------------------------------------
    def create_or_update_skill_progress(self, skill: SkillProgress) -> SkillProgress:
        existing = (
            self.db.query(SkillProgress)
            .filter(SkillProgress.user_id == skill.user_id, SkillProgress.skill_name == skill.skill_name)
            .first()
        )
        if existing:
            existing.confidence_score = skill.confidence_score
            existing.evidence_score = skill.evidence_score
            existing.assessment_score = skill.assessment_score
            existing.project_score = skill.project_score
            existing.status = skill.status
            existing.recorded_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)
            return skill

    def list_skill_progress(self, user_id: int) -> List[SkillProgress]:
        return (
            self.db.query(SkillProgress)
            .filter(SkillProgress.user_id == user_id)
            .order_by(SkillProgress.confidence_score.desc())
            .all()
        )

    # ------------------------------------------------------------------------
    # Career Reviews
    # ------------------------------------------------------------------------
    def create_review(self, review: CareerReview) -> CareerReview:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_latest_review(self, user_id: int) -> Optional[CareerReview]:
        return (
            self.db.query(CareerReview)
            .filter(CareerReview.user_id == user_id)
            .order_by(CareerReview.created_at.desc())
            .first()
        )

    def list_reviews(self, user_id: int) -> List[CareerReview]:
        return (
            self.db.query(CareerReview)
            .filter(CareerReview.user_id == user_id)
            .order_by(CareerReview.created_at.desc())
            .all()
        )

    # ------------------------------------------------------------------------
    # Career Risks
    # ------------------------------------------------------------------------
    def create_risk(self, risk: CareerRisk) -> CareerRisk:
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def list_active_risks(self, user_id: int) -> List[CareerRisk]:
        return (
            self.db.query(CareerRisk)
            .filter(CareerRisk.user_id == user_id, CareerRisk.status == "ACTIVE")
            .order_by(CareerRisk.created_at.desc())
            .all()
        )

    # ------------------------------------------------------------------------
    # Career Scenarios
    # ------------------------------------------------------------------------
    def create_scenario(self, scenario: CareerScenario) -> CareerScenario:
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def list_scenarios(self, user_id: int) -> List[CareerScenario]:
        return (
            self.db.query(CareerScenario)
            .filter(CareerScenario.user_id == user_id)
            .order_by(CareerScenario.created_at.desc())
            .all()
        )
