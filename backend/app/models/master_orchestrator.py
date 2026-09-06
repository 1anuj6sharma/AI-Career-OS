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


class MasterCareerPlan(Base):
    __tablename__ = "master_career_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_title = Column(String(200), nullable=False)
    strategy_summary = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, PAUSED, COMPLETED, RE_PLANNED
    version = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="master_career_plans")
    steps = relationship("MasterPlanStep", back_populates="plan", cascade="all, delete-orphan")


class MasterPlanStep(Base):
    __tablename__ = "master_plan_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(
        Integer,
        ForeignKey("master_career_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_name = Column(String(100), nullable=False, index=True)
    action_name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING", index=True)  # PENDING, IN_PROGRESS, COMPLETED, SKIPPED
    priority = Column(Integer, nullable=False, default=1)
    dependencies_json = Column(JSON, nullable=True)
    result_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("MasterCareerPlan", back_populates="steps")


class MasterCareerDecision(Base):
    __tablename__ = "master_career_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    decision_title = Column(String(200), nullable=False)
    reasoning = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=1)
    required_modules_json = Column(JSON, nullable=True)
    actions_json = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=False, default=0.9)
    status = Column(String(50), nullable=False, default="EXECUTED", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="master_career_decisions")


class MasterCareerEvent(Base):
    __tablename__ = "master_career_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(100), nullable=False, index=True)
    source_module = Column(String(100), nullable=False, index=True)
    payload_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="master_career_events")


class MasterCareerMemory(Base):
    __tablename__ = "master_career_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    memory_type = Column(String(50), nullable=False, default="LONG_TERM", index=True)  # SHORT_TERM, LONG_TERM, SEMANTIC
    key = Column(String(200), nullable=False, index=True)
    content_json = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="master_career_memories")


class MasterCareerStrategy(Base):
    __tablename__ = "master_career_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number = Column(Integer, nullable=False, default=1)
    strategy_title = Column(String(200), nullable=False)
    objective = Column(Text, nullable=False)
    reasons_for_pivot = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="master_career_strategies")


class MasterApprovalRecord(Base):
    __tablename__ = "master_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_id = Column(String(100), nullable=False)
    action_type = Column(String(100), nullable=False)
    action_description = Column(Text, nullable=False)
    risk_level = Column(String(50), nullable=False, default="LEVEL_3")  # LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4
    status = Column(String(50), nullable=False, default="PENDING_APPROVAL", index=True)  # PENDING_APPROVAL, APPROVED, REJECTED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="master_approvals")
