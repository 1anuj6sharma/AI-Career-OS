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


class PortfolioProfile(Base):
    __tablename__ = "portfolio_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    target_role = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)  # DRAFT, PUBLISHED, ARCHIVED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="portfolio_profiles")
    projects = relationship(
        "PortfolioProject", back_populates="portfolio", cascade="all, delete-orphan"
    )


class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(
        Integer,
        ForeignKey("portfolio_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    architecture = Column(Text, nullable=True)
    technologies = Column(JSON, nullable=True)
    impact = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.9)
    display_order = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    portfolio = relationship("PortfolioProfile", back_populates="projects")


class CareerBrandProfile(Base):
    __tablename__ = "career_brand_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    brand_statement = Column(Text, nullable=False)
    target_role = Column(String(200), nullable=False)
    positioning = Column(Text, nullable=True)
    core_strengths = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="career_brand_profiles")


class BrandScore(Base):
    __tablename__ = "brand_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    portfolio_score = Column(Float, nullable=False, default=80.0)
    github_score = Column(Float, nullable=False, default=75.0)
    linkedin_score = Column(Float, nullable=False, default=70.0)
    project_score = Column(Float, nullable=False, default=85.0)
    overall_score = Column(Float, nullable=False, default=77.5)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="brand_scores")


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type = Column(String(50), nullable=False, default="ARTICLE")  # ARTICLE, LINKEDIN_POST, README, PROJECT_ANNOUNCEMENT
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)  # DRAFT, IN_REVIEW, APPROVED, PUBLISHED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="content_items")


class GitHubAnalysis(Base):
    __tablename__ = "github_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    repository_count = Column(Integer, nullable=False, default=0)
    activity_score = Column(Float, nullable=False, default=0.0)
    documentation_score = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="github_analyses")


class ProfileRecommendation(Base):
    __tablename__ = "profile_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform = Column(String(50), nullable=False, default="LINKEDIN")  # LINKEDIN, PORTFOLIO, GITHUB
    recommendation_type = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False, default="HIGH")
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, APPLIED, DISMISSED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="profile_recommendations")
