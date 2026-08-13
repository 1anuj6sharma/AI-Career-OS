from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_role = Column(String(200), nullable=False)
    objective = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, ADAPTED, COMPLETED, ARCHIVED
    version = Column(Integer, nullable=False, default=1)
    roadmap_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="career_roadmaps")
    milestones = relationship(
        "CareerMilestone", back_populates="roadmap", cascade="all, delete-orphan"
    )
    adaptations = relationship(
        "CareerAdaptation", back_populates="roadmap", cascade="all, delete-orphan"
    )


class CareerMilestone(Base):
    __tablename__ = "career_milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column(
        Integer,
        ForeignKey("career_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    priority = Column(String(50), nullable=False, default="HIGH")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roadmap = relationship("CareerRoadmap", back_populates="milestones")


class CareerAdaptation(Base):
    __tablename__ = "career_adaptations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column(
        Integer,
        ForeignKey("career_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number = Column(Integer, nullable=False, default=1)
    reason = Column(Text, nullable=False)
    adaptation_summary = Column(Text, nullable=False)
    changes_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roadmap = relationship("CareerRoadmap", back_populates="adaptations")
