from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.agents.planner_agent import CareerPlannerAgent
from app.modules.career.agents.skill_gap_agent import Module7SkillGapAgent
from app.modules.career.agents.task_planner_agent import TaskPlanningAgent
from app.modules.career.agents.progress_analyzer_agent import ProgressAnalyzerAgent
from app.modules.career.agents.feedback_agent import FeedbackAgent
from app.modules.career.agents.adaptation_agent import AdaptationAgent
from app.modules.career.tools.career_tools import get_user_career_goal_data, calculate_career_hard_metrics


class CareerOrchestratorAgent:
    """
    Agent 1: Career Orchestrator Agent
    Main coordinator directing events, skill gaps, task creation, and closed-loop roadmap adaptation.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute_closed_loop(self, db: Session, user_id: int, target_role: str = None) -> Dict[str, Any]:
        # 1. Load User Goal & Metrics
        goal_data = get_user_career_goal_data(db, user_id)
        role = target_role or goal_data["target_role"]
        metrics = calculate_career_hard_metrics(db, user_id)

        # 2. Skill Gap Agent
        skill_agent = Module7SkillGapAgent(self.llm_service)
        gaps = skill_agent.run(role, goal_data["current_skills"])

        # 3. Career Planner Agent
        planner = CareerPlannerAgent(self.llm_service)
        roadmap = planner.run(role, goal_data["current_skills"])

        # 4. Schedule Tasks for Phase 1 via TaskPlanningAgent
        task_agent = TaskPlanningAgent(self.llm_service)
        tasks_created = 0
        if roadmap.milestones:
            m1 = roadmap.milestones[0]
            tasks_list = [t.model_dump() for t in m1.tasks]
            tasks_created = task_agent.run(db, user_id, m1.title, tasks_list)

        # 5. Adaptation Agent (Closed-loop check)
        adapter = AdaptationAgent(self.llm_service)
        adaptation = adapter.run(metrics, current_roadmap_version=1)

        return {
            "target_role": role,
            "roadmap": roadmap.model_dump(),
            "skill_gaps": gaps,
            "metrics": metrics,
            "tasks_created": tasks_created,
            "adaptation": adaptation,
        }
