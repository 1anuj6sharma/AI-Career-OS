from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.opportunities.agents import (
    JobParserAgent,
    MatchingAgent,
    OpportunitySkillGapAgent,
    CompanyAgent,
    RankingAgent,
    ReadinessAgent,
    StrategyAgent,
)
from app.modules.opportunities.tools.opportunity_tools import get_user_candidate_context


class OpportunityGraphOrchestrator:
    """
    Module 10 LangGraph Stateful Workflow Engine.
    Orchestrates job parsing, multi-dimensional matching, readiness score routing (APPLY NOW vs PREPARE THEN APPLY vs PREPARE FIRST), company research (with safe fallback recovery), and strategy generation.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = JobParserAgent(llm_service)
        self.matcher = MatchingAgent(llm_service)
        self.gap_agent = OpportunitySkillGapAgent(llm_service)
        self.company_agent = CompanyAgent(llm_service)
        self.ranking_agent = RankingAgent(llm_service)
        self.readiness_agent = ReadinessAgent(llm_service)
        self.strategy_agent = StrategyAgent(llm_service)

    def route_after_readiness(self, readiness_score: float) -> str:
        """Conditional routing based on readiness score threshold."""
        if readiness_score >= 80.0:
            return "recommend_apply"
        elif readiness_score >= 60.0:
            return "recommend_improvement"
        return "recommend_prepare"

    def run_opportunity_pipeline(
        self, db: Session, user_id: int, raw_description: str, title: str = "Backend Engineer", company_name: str = "TechCorp"
    ) -> Dict[str, Any]:
        # 1. Parse Job Description
        parsed = self.parser.run(raw_description, title)

        # 2. Fetch User Candidate Context
        c_ctx = get_user_candidate_context(db, user_id)

        # 3. Multi-dimensional Matching Engine
        match_res = self.matcher.run(
            candidate_skills=c_ctx["skills"],
            candidate_exp=c_ctx["total_experience_years"],
            required_skills=parsed["required_skills"],
            preferred_skills=parsed["preferred_skills"],
            min_exp=parsed["min_experience_years"],
        )

        # 4. Readiness Evaluation & Routing
        readiness_res = self.readiness_agent.run(match_res)
        route_decision = self.route_after_readiness(readiness_res["readiness_score"])

        # 5. Skill Gap Analysis for Modules 7 & 8
        gap_res = self.gap_agent.run(match_res.get("missing_skills", []), title)

        # 6. Company Research (Safe fallback handling)
        comp_res = self.company_agent.run(company_name)

        # 7. Application Strategy Generation
        strat_res = self.strategy_agent.run(title, match_res.get("missing_skills", []), readiness_res)

        return {
            "parsed_job": parsed,
            "match_breakdown": match_res,
            "readiness": readiness_res,
            "routing_strategy": route_decision,
            "cross_module_gaps": gap_res,
            "company_intelligence": comp_res,
            "application_strategy": strat_res,
        }
