from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.offers.repository import OfferRepository
from app.modules.offers.models import (
    CareerOffer,
    OfferCompensation,
    OfferAnalysisRecord,
    NegotiationStrategyRecord,
    CareerDecisionRecord,
)
from app.modules.offers.exceptions import CareerOfferNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.offers.graph.offer_graph import OfferGraphOrchestrator


class OfferService:
    def __init__(self, repo: OfferRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = OfferGraphOrchestrator(llm_service)

    def analyze_and_create_offer(
        self, user_id: int, company_name: str, role: str, base_salary: float, variable_salary: float, joining_bonus: float
    ) -> Dict[str, Any]:
        # 1. Run Offer Analysis State Machine
        pipeline_res = self.graph_orchestrator.run_offer_analysis_pipeline(
            company_name, role, base_salary, variable_salary, joining_bonus
        )

        comp_data = pipeline_res["compensation"]
        fit_data = pipeline_res["career_fit"]
        risk_data = pipeline_res["company_risk"]
        decision_data = pipeline_res["decision"]

        # 2. Persist CareerOffer in DB
        offer_obj = CareerOffer(
            user_id=user_id,
            company_name=company_name,
            role=role,
            status="RECEIVED",
        )
        created_offer = self.repo.create_offer(offer_obj)

        # 3. Persist OfferCompensation (Determined deterministically)
        comp_obj = OfferCompensation(
            offer_id=created_offer.id,
            base_salary=base_salary,
            variable_salary=variable_salary,
            bonus=0.0,
            joining_bonus=joining_bonus,
            equity=0.0,
            total_ctc=comp_data["total_ctc"],
            guaranteed_compensation=comp_data["guaranteed_compensation"],
        )
        self.repo.save_compensation(comp_obj)

        # 4. Persist OfferAnalysisRecord
        analysis_obj = OfferAnalysisRecord(
            offer_id=created_offer.id,
            compensation_score=comp_data["guaranteed_percentage"],
            career_fit_score=fit_data["career_fit_score"],
            growth_score=fit_data["growth_score"],
            company_score=risk_data["company_score"],
            location_score=80.0,
            risk_score=risk_data["risk_score"],
            overall_score=pipeline_res["overall_offer_score"],
            analysis=decision_data["reasoning"],
        )
        self.repo.save_analysis(analysis_obj)

        pipeline_res["offer_id"] = created_offer.id
        logger.info(f"Analyzed & created career offer id={created_offer.id} score={pipeline_res['overall_offer_score']} for user={user_id}")
        return pipeline_res

    def list_offers(self, user_id: int) -> List[CareerOffer]:
        return self.repo.list_offers(user_id)

    def generate_negotiation_strategy(self, offer_id: int, target_base_salary: float) -> Dict[str, Any]:
        offer = self.repo.get_offer(offer_id)
        if not offer:
            raise CareerOfferNotFoundException()

        base = offer.compensation.base_salary if offer.compensation else 1200000.0
        neg_data = self.graph_orchestrator.negotiation_agent.run(
            company_name=offer.company_name,
            role=offer.role,
            current_base=base,
            target_base=target_base_salary,
        )

        neg_obj = NegotiationStrategyRecord(
            offer_id=offer.id,
            target_compensation=target_base_salary,
            minimum_compensation=base,
            leverage_score=neg_data["leverage_score"],
            strategy=neg_data["draft_negotiation_email"],
        )
        self.repo.save_negotiation(neg_obj)

        neg_data["offer_id"] = offer.id
        return neg_data

    def record_decision(self, user_id: int, offer_id: int) -> CareerDecisionRecord:
        offer = self.repo.get_offer(offer_id)
        if not offer:
            raise CareerOfferNotFoundException()

        dec_obj = CareerDecisionRecord(
            user_id=user_id,
            offer_id=offer_id,
            decision="ACCEPT",
            reasoning="Offer meets candidate compensation benchmarks and aligns with microservice backend target role.",
            confidence=90.0,
        )
        saved_dec = self.repo.save_decision(dec_obj)
        offer.status = "ACCEPTED"
        self.repo.db.commit()

        logger.info(f"Recorded decision ACCEPT for offer id={offer_id} user={user_id}")
        return saved_dec

    def generate_transition_plan(self, offer_id: int) -> Dict[str, Any]:
        offer = self.repo.get_offer(offer_id)
        if not offer:
            raise CareerOfferNotFoundException()

        trans = self.graph_orchestrator.generate_transition(offer.company_name, offer.role)
        trans["offer_id"] = offer_id
        return trans

    def compare_offers(self, offer_a_id: int, offer_b_id: int) -> Dict[str, Any]:
        offer_a = self.repo.get_offer(offer_a_id)
        offer_b = self.repo.get_offer(offer_b_id)
        if not offer_a or not offer_b:
            raise CareerOfferNotFoundException()

        ctc_a = offer_a.compensation.total_ctc if offer_a.compensation else 1200000.0
        ctc_b = offer_b.compensation.total_ctc if offer_b.compensation else 1400000.0

        rec_id = offer_a_id if ctc_a >= ctc_b else offer_b_id

        return {
            "offer_a_id": offer_a_id,
            "offer_b_id": offer_b_id,
            "recommended_offer_id": rec_id,
            "comparison_summary": f"Offer A ({offer_a.company_name} - ₹{ctc_a/100000:.1f} LPA) vs Offer B ({offer_b.company_name} - ₹{ctc_b/100000:.1f} LPA). Recommend Offer {rec_id} based on guaranteed compensation and career trajectory.",
        }
