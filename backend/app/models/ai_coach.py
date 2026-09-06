from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class CareerHealthScore(Base):
    __tablename__ = "career_health_scores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    total_score = Column(Integer, default=0)
    skills_score = Column(Integer, default=0)
    resume_score = Column(Integer, default=0)
    portfolio_score = Column(Integer, default=0)
    interview_score = Column(Integer, default=0)
    market_alignment_score = Column(Integer, default=0)
    networking_score = Column(Integer, default=0)
    job_readiness_score = Column(Integer, default=0)
    learning_progress_score = Column(Integer, default=0)
    application_performance_score = Column(Integer, default=0)
    breakdown = Column(JSON, nullable=True)
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
class CareerMemory(Base):
    __tablename__ = "career_memories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    memory_type = Column(String(50)) # e.g. "goal", "weakness", "priority", "decision"
    content = Column(Text, nullable=False)
    context_data = Column(JSON, nullable=True) # Any structured metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CareerRecommendation(Base):
    """A durable, user-owned recommendation and its feedback loop."""
    __tablename__ = "career_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_type = Column(String(50), nullable=False, default="NEXT_ACTION")
    title = Column(String(300), nullable=False)
    rationale = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="MEDIUM")
    impact = Column(String(20), nullable=False, default="MEDIUM")
    effort = Column(String(20), nullable=False, default="MEDIUM")
    urgency = Column(String(20), nullable=False, default="MEDIUM")
    estimated_minutes = Column(Integer, nullable=False, default=30)
    confidence = Column(Integer, nullable=False, default=50)
    evidence = Column(JSON, nullable=True)
    task_id = Column(Integer, ForeignKey("career_tasks.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    feedback = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CareerCoachingSession(Base):
    """Stores concise coach exchanges without retaining unrelated chat noise."""
    __tablename__ = "career_coaching_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    intent = Column(String(50), nullable=False, default="CAREER")
    request = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context_summary = Column(JSON, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
