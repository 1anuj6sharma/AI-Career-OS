from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.brand.repository import BrandRepository
from app.modules.brand.models import (
    PortfolioProfile,
    PortfolioProject,
    CareerBrandProfile,
    BrandScore,
    ContentItem,
)
from app.modules.brand.exceptions import PortfolioNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.brand.graph.brand_graph import BrandGraphOrchestrator
from app.modules.career.models import CareerRoadmap
from app.modules.profile.models import Skill, Profile


class BrandService:
    def __init__(self, repo: BrandRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = BrandGraphOrchestrator(llm_service)

    def analyze_brand(
        self, db: Session, user_id: int, target_role: Optional[str] = None, github_username: Optional[str] = None
    ) -> Dict[str, Any]:
        active_roadmap = db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE").first()
        role = target_role or (active_roadmap.target_role if active_roadmap else "Backend Engineer")

        result = self.graph_orchestrator.run_brand_analysis_pipeline(db, user_id, role, github_username)

        scores_dict = result["scores"]
        score_obj = BrandScore(
            user_id=user_id,
            portfolio_score=scores_dict["portfolio_score"],
            github_score=scores_dict["github_score"],
            linkedin_score=scores_dict["linkedin_score"],
            project_score=scores_dict["project_score"],
            overall_score=scores_dict["overall_score"],
        )
        self.repo.save_brand_score(score_obj)

        return result

    def generate_portfolio(
        self, db: Session, user_id: int, target_role: Optional[str] = None
    ) -> PortfolioProfile:
        active_roadmap = db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE").first()
        role = target_role or (active_roadmap.target_role if active_roadmap else "Backend Engineer")

        skills = db.query(Skill).filter(Skill.user_id == user_id).all()
        skill_names = [s.name for s in skills] or ["Python", "FastAPI", "Docker", "PostgreSQL"]

        raw_projects = [{"title": "AI Career OS Engine", "tech": skill_names}]

        portfolio_data = self.graph_orchestrator.generate_portfolio_pipeline(role, skill_names, raw_projects)

        new_portfolio = PortfolioProfile(
            user_id=user_id,
            title=portfolio_data.get("title", f"Portfolio for {role}"),
            bio=portfolio_data.get("bio", f"Experienced {role}"),
            target_role=role,
            status="PUBLISHED",
        )
        created_p = self.repo.create_portfolio(new_portfolio)

        for idx, p in enumerate(portfolio_data.get("projects", []), 1):
            project_obj = PortfolioProject(
                portfolio_id=created_p.id,
                title=p.get("title", "Project Case Study"),
                description=p.get("description", ""),
                architecture=p.get("architecture", ""),
                technologies=p.get("technologies", skill_names),
                impact=p.get("impact", ""),
                confidence_score=p.get("confidence_score", 0.95),
                display_order=idx,
            )
            self.repo.create_project(project_obj)

        logger.info(f"Generated portfolio profile id={created_p.id} for user={user_id}")
        return self.repo.get_active_portfolio(user_id)

    def get_active_portfolio(self, user_id: int) -> PortfolioProfile:
        portfolio = self.repo.get_active_portfolio(user_id)
        if not portfolio:
            raise PortfolioNotFoundException()
        return portfolio

    def optimize_linkedin(self, db: Session, user_id: int) -> Dict[str, Any]:
        active_roadmap = db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE").first()
        role = active_roadmap.target_role if active_roadmap else "Backend Engineer"

        skills = db.query(Skill).filter(Skill.user_id == user_id).all()
        skill_names = [s.name for s in skills] or ["Python", "FastAPI", "Docker", "PostgreSQL"]

        return self.graph_orchestrator.optimize_linkedin_pipeline(role, skill_names)

    def generate_content(self, user_id: int, content_type: str, topic: str) -> ContentItem:
        res = self.graph_orchestrator.generate_content_pipeline(user_id, content_type, topic)

        item = ContentItem(
            user_id=user_id,
            content_type=content_type,
            title=res.get("title", topic),
            content=res.get("content", ""),
            status="DRAFT",
        )
        return self.repo.create_content_item(item)

    def list_content_items(self, user_id: int) -> List[ContentItem]:
        return self.repo.list_content_items(user_id)
