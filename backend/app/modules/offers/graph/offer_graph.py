from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.offers.agents import (
    OfferParserAgent,
    CompensationAgent,
    MarketBenchmarkAgent,
    CareerFitAgent,
    OfferCompanyAgent,
    NegotiationAgent,
    CareerDecisionAgent,
    TransitionAgent,
)


class OfferGraphOrchestrator:
    """
    Module 12 LangGraph Stateful Decision Engine.
    Orchestrates offer parsing, deterministic compensation calculation, market benchmarking, risk analysis, multi-dimensional scoring, decision recommendation (ACCEPT / NEGOTIATE / WAIT / REJECT), and transition planning.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.parser = OfferParserAgent(llm_service)
        self.comp_agent = CompensationAgent(llm_service)
        self.market_agent = MarketBenchmarkAgent(llm_service)
        self.career_fit_agent = CareerFitAgent(llm_service)
        self.company_agent = OfferCompanyAgent(llm_service)
        self.negotiation_agent = NegotiationAgent(llm_service)
        self.decision_agent = CareerDecisionAgent(llm_service)
        self.transition_agent = TransitionAgent(llm_service)

    def route_decision(self, decision: str) -> str:
        """Conditional routing based on decision recommendation."""
        d = decision.upper()
        if d == "ACCEPT":
            return "accept"
        elif d == "NEGOTIATE":
            return "negotiate"
        elif d == "WAIT":
            return "wait"
        return "reject"

    def run_offer_analysis_pipeline(
        self, company_name: str, role: str, base_salary: float, variable_salary: float, joining_bonus: float
    ) -> Dict[str, Any]:
        # 1. Deterministic Compensation Calculation (No LLM math)
        comp_res = self.comp_agent.run(base_salary, variable_salary, joining_bonus)

        # 2. Market Salary Benchmarking
        market_res = self.market_agent.run(role, base_salary)

        # 3. Career Fit & Growth Analysis
        fit_res = self.career_fit_agent.run(role, company_name)

        # 4. Company & Employment Risk Analysis
        risk_res = self.company_agent.run(company_name, comp_res["variable_percentage"])

        # 5. Multi-dimensional Offer Score Calculation
        overall_score = (
            comp_res["guaranteed_percentage"] * 0.30
            + fit_res["career_fit_score"] * 0.30
            + fit_res["growth_score"] * 0.20
            + risk_res["company_score"] * 0.20
        )

        # 6. Career Decision Recommendation & Routing
        decision_res = self.decision_agent.run(
            overall_score=overall_score,
            leverage_score=80.0,
            guaranteed_pct=comp_res["guaranteed_percentage"],
        )
        route_decision = self.route_decision(decision_res["decision"])

        # 7. Negotiation Strategy
        neg_res = self.negotiation_agent.run(
            company_name=company_name,
            role=role,
            current_base=base_salary,
            target_base=base_salary * 1.15,
        )

        return {
            "company_name": company_name,
            "role": role,
            "compensation": comp_res,
            "market_benchmark": market_res,
            "career_fit": fit_res,
            "company_risk": risk_res,
            "overall_offer_score": round(overall_score, 1),
            "decision": decision_res,
            "routing": route_decision,
            "negotiation_strategy": neg_res,
        }

    def generate_transition(self, company_name: str, role: str) -> Dict[str, Any]:
        return self.transition_agent.run(company_name, role)
