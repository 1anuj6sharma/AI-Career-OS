from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class AdaptiveLearningAgent:
    """
    Agent 6: Adaptive Learning Agent
    Detects repeated assessment failures, triggers prerequisite remediation, and adjusts learning content.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, topic_title: str, last_scores: List[float]) -> Dict[str, Any]:
        needs_remediation = any(s < 70.0 for s in last_scores) if last_scores else False

        prompt = f"""
        Act as an Adaptive Pedagogical Specialist.
        Evaluate if candidate needs prerequisite remediation for '{topic_title}':

        Recent Assessment Scores: {last_scores}

        If scores are below 70%, generate a simplified breakdown of foundational concepts.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "AdaptiveLearningAgent",
            "remediation_required": needs_remediation,
            "remedial_topic": f"Foundations of {topic_title}" if needs_remediation else None,
            "remediation_plan": getattr(response, "content", str(response)),
        }
