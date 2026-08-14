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
    goal_id = Column(
        Integer,
        ForeignKey("career_goals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    priority = Column(String(50), nullable=False, default="HIGH")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roadmap = relationship("CareerRoadmap", back_populates="milestones")
    goal = relationship("CareerGoal", back_populates="milestones")
    tasks = relationship("CareerTask", back_populates="milestone", cascade="all, delete-orphan")


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


# ============================================================================
# MODULE 13 — PERFORMANCE, PRODUCTIVITY & CONTINUOUS GROWTH ENTITIES
# ============================================================================

class CareerGoal(Base):
    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(String(50), nullable=False, default="LONG_TERM", index=True) # LONG_TERM, SHORT_TERM, SKILL_ACQUISITION
    priority = Column(String(50), nullable=False, default="HIGH") # HIGH, MEDIUM, LOW
    status = Column(String(50), nullable=False, default="ACTIVE", index=True) # ACTIVE, COMPLETED, ARCHIVED
    target_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="career_goals")
    milestones = relationship("CareerMilestone", back_populates="goal")
    tasks = relationship("CareerTask", back_populates="goal")


class CareerTask(Base):
    __tablename__ = "career_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    milestone_id = Column(
        Integer,
        ForeignKey("career_milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    goal_id = Column(
        Integer,
        ForeignKey("career_goals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), nullable=False, default="MEDIUM") # HIGH, MEDIUM, LOW
    status = Column(String(50), nullable=False, default="PENDING", index=True) # PENDING, IN_PROGRESS, COMPLETED, POSTPONED
    estimated_minutes = Column(Integer, nullable=False, default=30)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="career_tasks")
    milestone = relationship("CareerMilestone", back_populates="tasks")
    goal = relationship("CareerGoal", back_populates="tasks")


class CareerProgress(Base):
    __tablename__ = "career_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True) # GOAL_PROGRESS, SKILL_DEV, PROJECT_EXEC, LEARNING_CONSISTENCY, CAREER_ACTIVITIES, MILESTONE_PROGRESS
    score = Column(Float, nullable=False, default=0.0)
    measurement = Column(JSON, nullable=True)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", backref="career_progress_records")


class SkillProgress(Base):
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name = Column(String(100), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False, default=50.0)
    evidence_score = Column(Float, nullable=False, default=50.0)
    assessment_score = Column(Float, nullable=False, default=50.0)
    project_score = Column(Float, nullable=False, default=50.0)
    status = Column(String(50), nullable=False, default="STABLE", index=True) # IMPROVING, STABLE, DECLINING, UNTESTED

    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="skill_progress_records")


class CareerReview(Base):
    __tablename__ = "career_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    review_type = Column(String(50), nullable=False, default="WEEKLY", index=True) # DAILY, WEEKLY, MONTHLY, MILESTONE
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    performance_score = Column(Float, nullable=False, default=80.0)
    summary = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="career_reviews")


class CareerRisk(Base):
    __tablename__ = "career_risks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True) # ACTIVE, MITIGATED, ARCHIVED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="career_risks")


class CareerScenario(Base):
    __tablename__ = "career_scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_name = Column(String(200), nullable=False)
    target_role = Column(String(200), nullable=False)
    assumptions = Column(JSON, nullable=True)
    projection = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="career_scenarios")
