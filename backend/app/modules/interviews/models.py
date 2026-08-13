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


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resume_version_id = Column(
        Integer,
        ForeignKey("resume_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(200), nullable=False)
    company_name = Column(String(150), nullable=True)
    interview_type = Column(String(50), nullable=False, default="TECHNICAL")  # TECHNICAL, BEHAVIORAL, SYSTEM_DESIGN, HR
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="SCHEDULED", index=True)  # SCHEDULED, PREPARING, IN_PROGRESS, COMPLETED, CANCELLED
    overall_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="interviews")
    job = relationship("Job", backref="interviews")
    resume_version = relationship("ResumeVersion", backref="interviews")
    questions = relationship(
        "InterviewQuestion", back_populates="interview", cascade="all, delete-orphan"
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="TECHNICAL")
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=False, default="MEDIUM")
    expected_time_minutes = Column(Integer, nullable=False, default=15)
    evaluation_criteria = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interview = relationship("Interview", back_populates="questions")
    answers = relationship(
        "InterviewAnswer", back_populates="question_obj", cascade="all, delete-orphan"
    )


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(
        Integer,
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer = Column(Text, nullable=False)
    duration_seconds = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question_obj = relationship("InterviewQuestion", back_populates="answers")
    evaluation = relationship(
        "AnswerEvaluation", back_populates="answer_obj", uselist=False, cascade="all, delete-orphan"
    )


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_id = Column(
        Integer,
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technical_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    depth_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=False, default=0.0)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    missing_points = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    answer_obj = relationship("InterviewAnswer", back_populates="evaluation")
