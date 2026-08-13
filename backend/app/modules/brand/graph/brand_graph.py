from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.brand.agents import (
    PortfolioAgent,
    ProjectShowcaseAgent,
    GitHubAgent,
    LinkedInAgent,
    ContentAgent,
    BrandAnalyzerAgent,
    VisibilityAgent,
)


class BrandGraphOrchestrator:
    """
    Module 9 LangGraph Stateful Workflow Engine.
    Orchestrates brand analysis, portfolio optimization, GitHub analysis (with safe fallback recovery), LinkedIn profile optimization, content generation, and cross-module visibility recommendations.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.portfolio_agent = PortfolioAgent(llm_service)
        self.project_agent = ProjectShowcaseAgent(llm_service)
        self.github_agent = GitHubAgent(llm_service)
        self.linkedin_agent = LinkedInAgent(llm_service)
        self.content_agent = ContentAgent(llm_service)
        self.analyzer_agent = BrandAnalyzerAgent(llm_service)
        self.visibility_agent = VisibilityAgent(llm_service)

    def route_brand_optimization(self, visibility_score: float) -> str:
        """Conditional routing based on visibility score threshold."""
        if visibility_score < 50.0:
            return "major_optimization"
        elif visibility_score < 75.0:
            return "moderate_optimization"
        return "minor_optimization"

    def run_brand_analysis_pipeline(
        self, db: Session, user_id: int, target_role: str = "Backend Engineer", github_username: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. GitHub Analysis (Handles missing/failed GitHub gracefully)
        github_res = self.github_agent.run(github_username)

        # 2. Brand Analyzer
        brand_res = self.analyzer_agent.run(db, user_id, target_role)

        # 3. Visibility Analysis & Cross-Module Recommendations
        visibility_res = self.visibility_agent.run(target_role, brand_res["scores"])

        # 4. Conditional Routing
        route_decision = self.route_brand_optimization(brand_res["scores"]["overall_score"])

        return {
            "target_role": target_role,
            "brand_statement": brand_res["brand_statement"],
            "scores": brand_res["scores"],
            "github_analysis": github_res,
            "visibility_gaps": visibility_res["visibility_gaps"],
            "recommendations": visibility_res["recommendations"],
            "routing_strategy": route_decision,
        }

    def generate_portfolio_pipeline(
        self, target_role: str, user_skills: List[str], raw_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        p_info = self.portfolio_agent.run(target_role, user_skills)

        case_studies = []
        for p in raw_projects:
            cs = self.project_agent.run(p)
            case_studies.append(cs)

        if not case_studies:
            # Fallback default project case study
            case_studies.append(self.project_agent.run({"title": "AI Career OS Platform"}))

        p_info["projects"] = case_studies
        return p_info

    def optimize_linkedin_pipeline(self, target_role: str, user_skills: List[str]) -> Dict[str, Any]:
        return self.linkedin_agent.run(target_role, user_skills)

    def generate_content_pipeline(self, user_id: int, content_type: str, topic: str) -> Dict[str, Any]:
        return self.content_agent.run(user_id, content_type, topic)
