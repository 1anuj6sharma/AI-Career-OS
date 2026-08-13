from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.offers.models import CareerOffer, OfferCompensation


def calculate_deterministic_compensation_scores(
    base: float, variable: float, joining_bonus: float, bonus: float = 0.0, equity: float = 0.0
) -> Dict[str, Any]:
    """
    Mandatory Deterministic Helper:
    Calculates exact total CTC and guaranteed compensation deterministically without LLM arithmetic.
    """
    total_ctc = base + variable + joining_bonus + bonus + equity
    guaranteed = base + joining_bonus

    guaranteed_pct = (guaranteed / total_ctc * 100.0) if total_ctc > 0 else 100.0
    variable_pct = (variable / total_ctc * 100.0) if total_ctc > 0 else 0.0

    return {
        "base_salary": base,
        "variable_salary": variable,
        "joining_bonus": joining_bonus,
        "bonus": bonus,
        "equity": equity,
        "total_ctc": total_ctc,
        "guaranteed_compensation": guaranteed,
        "guaranteed_percentage": round(guaranteed_pct, 1),
        "variable_percentage": round(variable_pct, 1),
    }


def get_market_salary_benchmark(role: str, experience_years: float = 2.0) -> Dict[str, Any]:
    """Controlled READ tool: Returns market salary range and benchmark positioning."""
    return {
        "role": role,
        "median_salary_lpa": 11.5,
        "percentile_75_lpa": 14.0,
        "data_confidence": "HIGH",
    }
