from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class AIRun(Base):
    __tablename__ = "ai_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="RUNNING", index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)
    error = Column(Text, nullable=True)

    tool_calls = relationship(
        "AIToolCall", back_populates="run", cascade="all, delete-orphan"
    )
    user = relationship("User", backref="ai_runs")


class AIToolCall(Base):
    __tablename__ = "ai_tool_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(
        Integer,
        ForeignKey("ai_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name = Column(String(100), nullable=False)
    input_params = Column(JSON, nullable=True)
    output_result = Column(JSON, nullable=True)
    status = Column(String(50), default="SUCCESS")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    run = relationship("AIRun", back_populates="tool_calls")


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False, default="Career Copilot Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    messages = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
    user = relationship("User", backref="ai_conversations")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        Integer,
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender = Column(String(50), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("AIConversation", back_populates="messages")


class AIMemory(Base):
    __tablename__ = "ai_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    memory_type = Column(String(50), nullable=False, default="PREFERENCE")  # "PREFERENCE", "SKILL_GOAL", "NOTE"
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="ai_memories")


class AIPendingAction(Base):
    __tablename__ = "ai_pending_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id = Column(Integer, ForeignKey("ai_runs.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(100), nullable=False)  # e.g., "UPDATE_APPLICATION_STATUS", "DELETE_JOB", "SEND_EMAIL"
    description = Column(Text, nullable=False)
    payload = Column(JSON, nullable=False)
    is_approved = Column(Boolean, default=False)
    is_executed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="ai_pending_actions")
