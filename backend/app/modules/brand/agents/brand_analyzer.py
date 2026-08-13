from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.brand.tools.brand_tools import calculate_brand_scores_data


class BrandAnalyzerAgent:
    """
    Agent 6: Brand Analyzer Agent
    Computes explainable personal brand scores deterministically and detects positioning inconsistencies.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int, target_role: str = "Software Engineer") -> Dict[str, Any]:
        scores = calculate_brand_scores_data(db, user_id)

        prompt = f"""
        Act as a Principal Recruiter & Brand Auditor.
        Evaluate personal brand positioning for candidate targeting '{target_role}':

        Deterministic Scores:
        - Portfolio Score: {scores['portfolio_score']}
        - GitHub Score: {scores['github_score']}
        - LinkedIn Score: {scores['linkedin_score']}
        - Overall Score: {scores['overall_score']}

        Identify key brand positioning strengths and inconsistencies.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "BrandAnalyzerAgent",
            "target_role": target_role,
            "brand_statement": f"Specialized {target_role} focused on production-grade microservices and backend reliability.",
            "scores": scores,
            "analysis_details": getattr(response, "content", str(response)),
        }
