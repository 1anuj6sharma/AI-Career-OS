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


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(200), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=False, default="pdf")
    status = Column(String(50), nullable=False, default="PARSED", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="resumes")
    versions = relationship(
        "ResumeVersion", back_populates="resume", cascade="all, delete-orphan"
    )


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number = Column(Integer, nullable=False, default=1)
    version_name = Column(String(200), nullable=False, default="v1.0 Original")
    parent_version_id = Column(Integer, nullable=True)
    created_by = Column(String(50), nullable=False, default="USER")  # "USER" or "AI"
    generation_reason = Column(String(255), nullable=True)
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    change_summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # Raw / markdown text
    structured_data = Column(JSON, nullable=True)  # Parsed JSON structure
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="versions")
    job = relationship("Job", backref="resume_versions")
