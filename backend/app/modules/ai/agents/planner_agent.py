from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.tools.application_tools import get_active_applications_data
from app.modules.ai.tools.task_tools import create_ai_task_tool
from app.modules.ai.services.llm_service import LLMService


class PlannerAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, db: Session, user_id: int) -> Dict[str, Any]:
        applications = get_active_applications_data(db, user_id)

        # Create automated actionable follow-up task using controlled tool for active applications
        tasks_created = []
        for app in applications:
            if app["status"] in ["APPLIED", "INTERVIEW"]:
                task_info = create_ai_task_tool(
                    db=db,
                    user_id=user_id,
                    application_id=app["id"],
                    title=f"Follow-up / Prep for {app['status']} Stage",
                    description="AI Scheduled Action: Research company updates and prepare key project Talking Points.",
                    priority="HIGH",
                )
                tasks_created.append(task_info)

        prompt = f"""
        Act as an AI Executive Career Planner.
        Review current pipeline applications: {applications}
        Synthesize a daily prioritized schedule for the job seeker.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "PlannerAgent",
            "daily_plan": getattr(response, "content", str(response)),
            "tasks_scheduled": tasks_created,
        }
