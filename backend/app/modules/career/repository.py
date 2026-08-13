from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.career.models import CareerRoadmap, CareerMilestone, CareerAdaptation


class CareerRepository:
    def __init__(self, db: Session):
        self.db = db

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
