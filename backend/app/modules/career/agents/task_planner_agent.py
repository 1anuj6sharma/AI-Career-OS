from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.tools.career_tools import schedule_career_tasks_tool


class TaskPlanningAgent:
    """
    Agent 4: Task Planning Agent
    Converts roadmap milestones into actionable tasks using Module 3's task system.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        db: Session,
        user_id: int,
        milestone_title: str,
        tasks_list: List[Dict[str, Any]],
    ) -> int:
        return schedule_career_tasks_tool(
            db=db,
            user_id=user_id,
            milestone_title=milestone_title,
            tasks=tasks_list,
        )
