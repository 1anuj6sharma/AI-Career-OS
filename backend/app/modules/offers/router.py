from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.offers.dependencies import get_offer_service
from app.modules.offers.service import OfferService
from app.modules.offers.schemas import (
    CareerOfferCreate,
    CareerOfferOut,
    NegotiationGenerateQuery,
    NegotiationStrategyOut,
    CareerDecisionQuery,
    CareerDecisionOut,
    TransitionPlanOut,
    OfferCompareQuery,
    OfferCompareOut,
)

router = APIRouter(prefix="/offers", tags=["Module 12 — AI Offer Management, Salary Negotiation & Career Decision Engine"])


@router.post(
    "/ai/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Parse offer details, compute deterministic compensation breakdown, multi-dimensional scoring, and decision recommendation",
)
def analyze_offer(
    payload: CareerOfferCreate,
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    return service.analyze_and_create_offer(
        user_id=current_user.id,
        company_name=payload.company_name,
        role=payload.role,
        base_salary=payload.base_salary,
        variable_salary=payload.variable_salary,
        joining_bonus=payload.joining_bonus,
    )


@router.get(
    "",
    response_model=List[CareerOfferOut],
    summary="List candidate career offers and evaluation details",
)
def list_offers(
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    return service.list_offers(current_user.id)


@router.post(
    "/ai/compare",
    response_model=OfferCompareOut,
    summary="Compare multiple competing job offers side-by-side",
)
def compare_offers(
    payload: OfferCompareQuery,
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    return service.compare_offers(payload.offer_a_id, payload.offer_b_id)


@router.post(
    "/ai/negotiate",
    response_model=NegotiationStrategyOut,
    summary="Generate negotiation strategy and email draft requiring explicit human review and approval",
)
def generate_negotiation_strategy(
    payload: NegotiationGenerateQuery,
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    return service.generate_negotiation_strategy(payload.offer_id, payload.target_base_salary)


@router.post(
    "/ai/decision",
    response_model=CareerDecisionOut,
    summary="Submit candidate final career decision (ACCEPT, NEGOTIATE, WAIT, REJECT)",
)
def record_decision(
    payload: CareerDecisionQuery,
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    saved = service.record_decision(current_user.id, payload.offer_id)
    return {
        "offer_id": payload.offer_id,
        "decision": saved.decision,
        "reasoning": saved.reasoning,
        "confidence": saved.confidence,
    }


@router.post(
    "/ai/transition-plan",
    response_model=TransitionPlanOut,
    summary="Generate 30/60/90-day onboarding and career transition plan after offer acceptance",
)
def generate_transition_plan(
    payload: CareerDecisionQuery,
    current_user: User = Depends(get_current_active_user),
    service: OfferService = Depends(get_offer_service),
):
    return service.generate_transition_plan(payload.offer_id)
