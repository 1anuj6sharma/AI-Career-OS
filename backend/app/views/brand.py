from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PortfolioProjectSchema(BaseModel):
    title: str = Field(..., example="AI Career OS Engine")
    description: str = Field(..., example="Full-stack AI-driven career management platform built with FastAPI, LangGraph, and PostgreSQL.")
    architecture: Optional[str] = "Modular microservices with vector search and stateful LangGraph agents"
    technologies: List[str] = ["Python", "FastAPI", "Docker", "PostgreSQL", "LangChain", "LangGraph"]
    impact: Optional[str] = "Accelerates job tracking and interview preparation by 4x"
    confidence_score: float = 0.95


class PortfolioProfileOut(BaseModel):
    id: int
    user_id: int
    title: str
    bio: Optional[str] = None
    target_role: str
    status: str
    projects: List[PortfolioProjectSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandScoreOut(BaseModel):
    portfolio_score: float
    github_score: float
    linkedin_score: float
    project_score: float
    overall_score: float


class GitHubAnalysisOut(BaseModel):
    repository_count: int
    activity_score: float
    documentation_score: float
    overall_score: float
    status: str = "AVAILABLE"  # AVAILABLE or UNAVAILABLE


class LinkedInOptimizeOut(BaseModel):
    current_headline_analysis: str
    suggested_headline: str
    suggested_about: str
    keyword_gaps: List[str] = []
    alignment_score: float


class ContentGenerateQuery(BaseModel):
    content_type: str = Field("ARTICLE", example="ARTICLE")  # ARTICLE, LINKEDIN_POST, README, PROJECT_ANNOUNCEMENT
    topic: str = Field("Building Scalable APIs with FastAPI and Docker", example="Building Scalable APIs with FastAPI and Docker")


class ContentItemOut(BaseModel):
    id: int
    user_id: int
    content_type: str
    title: str
    content: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandAnalysisOut(BaseModel):
    target_role: str
    brand_statement: str
    scores: BrandScoreOut
    visibility_gaps: List[str] = []
    recommendations: List[str] = []
    confidence_level: str = "HIGH"
