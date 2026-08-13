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


class JobOpportunity(Base):
    __tablename__ = "job_opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False, default="USER_IMPORTED")  # LINKEDIN, CAREER_PAGE, API, USER_IMPORTED
    external_job_id = Column(String(200), nullable=True)
    company_name = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=True)
    remote_status = Column(String(50), nullable=False, default="HYBRID")  # REMOTE, HYBRID, ON_SITE
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    employment_type = Column(String(50), nullable=False, default="FULL_TIME")

    posted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    requirements = relationship(
        "JobRequirementItem", back_populates="job", cascade="all, delete-orphan"
    )
    matches = relationship(
        "JobMatch", back_populates="job", cascade="all, delete-orphan"
    )


class JobRequirementItem(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill = Column(String(100), nullable=False)
    requirement_type = Column(String(50), nullable=False, default="REQUIRED")  # REQUIRED, PREFERRED, OPTIONAL
    importance = Column(Float, nullable=False, default=1.0)
    minimum_experience = Column(Float, nullable=True, default=0.0)

    job = relationship("JobOpportunity", back_populates="requirements")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_match = Column(Float, nullable=False, default=0.0)
    experience_match = Column(Float, nullable=False, default=0.0)
    project_match = Column(Float, nullable=False, default=0.0)
    resume_match = Column(Float, nullable=False, default=0.0)
    career_match = Column(Float, nullable=False, default=0.0)
    overall_match = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="job_matches")
    job = relationship("JobOpportunity", back_populates="matches")


class ApplicationReadiness(Base):
    __tablename__ = "application_readiness"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    readiness_score = Column(Float, nullable=False, default=0.0)
    resume_score = Column(Float, nullable=False, default=0.0)
    skill_score = Column(Float, nullable=False, default=0.0)
    project_score = Column(Float, nullable=False, default=0.0)
    interview_score = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="application_readiness")


class JobRecommendationRecord(Base):
    __tablename__ = "job_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recommendation = Column(String(100), nullable=False, default="PREPARE THEN APPLY")  # APPLY NOW, PREPARE THEN APPLY, PREPARE FIRST
    priority = Column(String(50), nullable=False, default="HIGH")
    reason = Column(Text, nullable=False)
    estimated_preparation_hours = Column(Integer, nullable=False, default=5)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="job_recommendation_records")


class CompanyIntelligenceRecord(Base):
    __tablename__ = "company_intelligence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False, index=True)
    technology_fit = Column(Float, nullable=False, default=80.0)
    career_growth = Column(Float, nullable=False, default=85.0)
    overall_fit = Column(Float, nullable=False, default=82.5)
    analysis = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
