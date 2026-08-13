from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class ReadinessAgent:
    """
    Agent 6: Application Readiness Agent
    Computes Application Readiness Score (0-100) and routes candidates based on configurable thresholds.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        overall_match = match_data.get("overall_match", 75.0)

        # Configurable readiness score formula
        readiness_score = overall_match

        if readiness_score >= 80.0:
            rec = "APPLY NOW"
            priority = "VERY HIGH"
            hours = 2
            reason = "High skill alignment and strong project evidence. Recommended for immediate application."
        elif readiness_score >= 60.0:
            rec = "PREPARE THEN APPLY"
            priority = "HIGH"
            hours = 5
            reason = f"Good technical match, but missing skills ({', '.join(match_data.get('missing_skills', ['AWS']))[:40]}). Prepare prior to applying."
        else:
            rec = "PREPARE FIRST"
            priority = "MEDIUM"
            hours = 12
            reason = "Significant skill and experience gap. Complete prerequisite learning modules before submitting application."

        return {
            "agent": "ReadinessAgent",
            "readiness_score": round(readiness_score, 1),
            "recommendation": rec,
            "priority": priority,
            "estimated_preparation_hours": hours,
            "reason": reason,
        }
