from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.learning.models import (
    LearningPath,
    LearningModule,
    LearningTopic,
    LearningResource,
    LearningAssessment,
    LearningNote,
)


class LearningRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_path(self, path: LearningPath) -> LearningPath:
        self.db.add(path)
        self.db.commit()
        self.db.refresh(path)
        return path

    def get_active_path(self, user_id: int) -> Optional[LearningPath]:
        return (
            self.db.query(LearningPath)
            .options(
                joinedload(LearningPath.modules)
                .joinedload(LearningModule.topics)
                .joinedload(LearningTopic.resources)
            )
            .filter(LearningPath.user_id == user_id, LearningPath.status == "ACTIVE")
            .order_by(LearningPath.created_at.desc())
            .first()
        )

    def list_paths(self, user_id: int) -> List[LearningPath]:
        return (
            self.db.query(LearningPath)
            .options(
                joinedload(LearningPath.modules)
                .joinedload(LearningModule.topics)
            )
            .filter(LearningPath.user_id == user_id)
            .order_by(LearningPath.created_at.desc())
            .all()
        )

    def create_module(self, module: LearningModule) -> LearningModule:
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def create_topic(self, topic: LearningTopic) -> LearningTopic:
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def create_resource(self, resource: LearningResource) -> LearningResource:
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def create_assessment(self, assessment: LearningAssessment) -> LearningAssessment:
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def archive_old_paths(self, user_id: int) -> None:
        self.db.query(LearningPath).filter(
            LearningPath.user_id == user_id, LearningPath.status == "ACTIVE"
        ).update({"status": "ARCHIVED"})
        self.db.commit()
