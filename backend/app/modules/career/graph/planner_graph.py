from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.agents import CareerOrchestratorAgent, CareerCoachAgent


class CareerGraphOrchestrator:
    """
    Module 7 LangGraph Stateful Workflow Engine.
    Orchestrates closed-loop career roadmap generation, task scheduling, progress tracking, and strategy adaptation.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.orchestrator_agent = CareerOrchestratorAgent(llm_service)
        self.coach_agent = CareerCoachAgent(llm_service)

    def run_execution_loop(self, db: Session, user_id: int, target_role: str = None) -> Dict[str, Any]:
        return self.orchestrator_agent.execute_closed_loop(db, user_id, target_role)

    def get_coach_response(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        return self.coach_agent.run(message, user_context)
