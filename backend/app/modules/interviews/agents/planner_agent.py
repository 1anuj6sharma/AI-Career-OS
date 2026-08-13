from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.interviews.tools.interview_tools import create_preparation_tasks_tool


class InterviewPlannerAgent:
    """
    Agent 8: Interview Planning Agent
    Generates a daily preparation plan and creates Module 3 tasks.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        db: Session,
        user_id: int,
        interview_id: int,
        interview_title: str,
        job_id: Optional[int],
        priority_topics: List[str],
        weak_topics: List[str] = None,
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Interview Schedule Planner.
        Create a 5-day action preparation plan for:

        Interview: {interview_title}
        Priority Technical Topics: {priority_topics}
        Weak Topics to Master: {weak_topics or []}

        Generate actionable tasks for Day 1 through Day 5.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        prep_tasks = [
            f"Review & Practice Core Topics: {', '.join(priority_topics[:2])}",
            f"System Design Mock Practice: {priority_topics[-1] if priority_topics else 'Architecture'}",
            f"STAR Behavioral Stories Refinement & Mock Recordings",
            f"Deep-dive practice on weak areas: {', '.join(weak_topics) if weak_topics else 'Edge Cases'}",
            f"Final Review & Company Tech Culture Briefing",
        ]

        # Schedule tasks in Module 3's task system via controlled tool
        tasks_created = create_preparation_tasks_tool(
            db=db,
            user_id=user_id,
            interview_title=interview_title,
            tasks=prep_tasks,
            job_id=job_id,
        )

        return {
            "agent": "InterviewPlannerAgent",
            "preparation_plan": prep_tasks,
            "tasks_created_count": tasks_created,
            "details": getattr(response, "content", str(response)),
        }
