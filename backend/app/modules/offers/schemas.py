from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CareerOfferCreate(BaseModel):
    company_name: str = Field("TechCorp", example="TechCorp")
    role: str = Field("Senior Python Backend Engineer", example="Senior Python Backend Engineer")
    base_salary: float = Field(1200000.0, example=1200000.0)  # INR ₹12 LPA
    variable_salary: float = Field(200000.0, example=200000.0)
    joining_bonus: float = Field(100000.0, example=100000.0)
    equity: float = Field(0.0, example=0.0)
    benefits: Optional[str] = "Health insurance, ₹50k learning allowance, hybrid work mode"


class OfferCompensationOut(BaseModel):
    base_salary: float
    variable_salary: float
    bonus: float
    joining_bonus: float
    equity: float
    total_ctc: float
    guaranteed_compensation: float

    model_config = ConfigDict(from_attributes=True)


class OfferAnalysisOut(BaseModel):
    compensation_score: float
    career_fit_score: float
    growth_score: float
    company_score: float
    location_score: float
    risk_score: float
    overall_score: float
    analysis: str

    model_config = ConfigDict(from_attributes=True)


class CareerOfferOut(BaseModel):
    id: int
    user_id: int
    company_name: str
    role: str
    status: str
    created_at: datetime
    compensation: Optional[OfferCompensationOut] = None
    analysis: Optional[OfferAnalysisOut] = None

    model_config = ConfigDict(from_attributes=True)


class NegotiationGenerateQuery(BaseModel):
    offer_id: int = Field(..., example=1)
    target_base_salary: float = Field(1400000.0, example=1400000.0)


class NegotiationStrategyOut(BaseModel):
    offer_id: int
    target_compensation: float
    minimum_compensation: float
    leverage_score: float
    primary_ask: str
    secondary_ask: str
    fallback_ask: str
    draft_negotiation_email: str


class CareerDecisionQuery(BaseModel):
    offer_id: int = Field(..., example=1)


class CareerDecisionOut(BaseModel):
    offer_id: int
    decision: str  # ACCEPT, NEGOTIATE, WAIT, REJECT
    reasoning: str
    confidence: float


class TransitionPlanOut(BaseModel):
    offer_id: int
    role: str
    company_name: str
    plan_30_days: List[str]
    plan_60_days: List[str]
    plan_90_days: List[str]


class OfferCompareQuery(BaseModel):
    offer_a_id: int = Field(..., example=1)
    offer_b_id: int = Field(..., example=2)


class OfferCompareOut(BaseModel):
    offer_a_id: int
    offer_b_id: int
    recommended_offer_id: int
    comparison_summary: str
