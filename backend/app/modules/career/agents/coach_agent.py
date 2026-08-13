from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class CareerCoachAgent:
    """
    User-Facing AI Career Coach Agent
    Grounded in candidate's roadmap, task progress, interview performance, and career goals.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as the Lead AI Career Coach for AI Career OS.
        Respond to candidate question grounded in actual user state:

        Candidate Question: "{message}"

        User System Context:
        - Target Role: {user_context.get('target_role', 'Software Engineer')}
        - Active Roadmap Version: {user_context.get('roadmap_version', 1)}
        - Task Completion Rate: {user_context.get('metrics', {}).get('task_completion_rate', 0)}%
        - Mock Interview Average: {user_context.get('metrics', {}).get('interview_score_avg', 0)}/100

        Provide direct, actionable, grounded coaching guidance without generic fluff.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "CareerCoachAgent",
            "reply": getattr(response, "content", str(response)),
            "recommended_tasks": [
                "Complete Docker multi-stage build milestone task",
                "Execute 1 live System Design AI Mock Interview",
            ],
            "adaptation_recommended": user_context.get("metrics", {}).get("task_completion_rate", 0) > 80.0,
        }
