from sqlalchemy import JSON, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database.base import Base

#: JSONB on PostgreSQL (indexable, the production dialect), plain JSON everywhere
#: else. A bare JSONB column cannot be compiled by SQLite, which broke the whole
#: test suite at table-creation time.
JSONVariant = JSON().with_variant(JSONB(), "postgresql")

class ExecutionPlan(Base):
    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    action = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # 1 = High, 2 = Medium, 3 = Low
    status = Column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, SKIPPED, EXECUTING
    source = Column(String, default="AI") # AI or USER
    expected_impact = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class ApprovalQueue(Base):
    __tablename__ = "approval_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    action_type = Column(String, nullable=False) # e.g. APPLY, MESSAGE, PROPOSAL
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    metadata_json = Column(JSONVariant, nullable=True) # stores draft data, application details, etc.
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

class CareerMemory(Base):
    __tablename__ = "career_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String, nullable=False) # e.g. ACTION_COMPLETED, SKILL_ADDED
    description = Column(Text, nullable=False)
    source = Column(String, nullable=True) # e.g. Dashboard, AI Orchestrator
    metadata_json = Column(JSONVariant, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
