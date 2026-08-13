from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class AdaptationAgent:
    """
    Agent 7: Adaptation Agent
    Closed-loop agent determining if active roadmap needs strategy pivot, priority shift, or goal adjustment.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, metrics: Dict[str, Any], current_roadmap_version: int) -> Dict[str, Any]:
        task_completion = metrics.get("task_completion_rate", 0)
        interview_score = metrics.get("interview_score_avg", 0)

        # Closed-loop adaptation logic: Trigger pivot if completion > 80% or interview score < 70
        needs_adaptation = task_completion > 80.0 or (interview_score > 0 and interview_score < 70.0)

        prompt = f"""
        Act as a Closed-Loop Career Adaptation Director.
        Evaluate if roadmap version {current_roadmap_version} requires adaptation:

        Metrics:
        - Task Completion: {task_completion}%
        - Interview Average: {interview_score}/100

        If tasks are completed or interview score indicates weakness, propose an updated strategic pivot.
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "AdaptationAgent",
            "adaptation_required": needs_adaptation,
            "proposed_version": current_roadmap_version + 1 if needs_adaptation else current_roadmap_version,
            "adaptation_reason": "High task execution velocity achieved; shifting active focus to System Design & Senior Architecture" if needs_adaptation else "Maintain active roadmap execution",
            "details": getattr(response, "content", str(response)),
        }
