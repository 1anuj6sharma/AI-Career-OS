from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class WeaknessDetectionAgent:
    """
    Agent 7: Weakness Detection Agent
    Identifies weak technical topics from evaluations and triggers adaptive questioning (follow-up depth or topic pivot).
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, evaluations_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        weak_topics = []
        strong_topics = []

        for item in evaluations_history:
            topic = item.get("topic", "General")
            score = item.get("score", 0.0)
            if score < 7.0:
                weak_topics.append(topic)
            elif score >= 8.5:
                strong_topics.append(topic)

        prompt = f"""
        Act as an Adaptive Interview Director.
        Analyze candidate performance across questions:

        Evaluations History: {evaluations_history}

        Identify:
        - Critical Weak Topics needing follow-up
        - Adaptive Routing Recommendation (e.g. increase difficulty on strong topics, drill down on weak topics)
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "WeaknessDetectionAgent",
            "weak_topics": list(set(weak_topics)),
            "strong_topics": list(set(strong_topics)),
            "adaptive_action": "DRILL_DOWN_WEAKNESS" if weak_topics else "INCREASE_DIFFICULTY",
            "recommendation": getattr(response, "content", str(response)),
        }
