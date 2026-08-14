from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.master_orchestrator.repository import MasterOrchestratorRepository
from app.modules.master_orchestrator.models import (
    MasterCareerPlan,
    MasterPlanStep,
    MasterCareerDecision,
    MasterCareerEvent,
    MasterCareerMemory,
    MasterCareerStrategy,
    MasterApprovalRecord,
)
from app.modules.ai.services.llm_service import LLMService
from app.modules.master_orchestrator.graph.master_graph import MasterGraphOrchestrator
from app.modules.master_orchestrator.services.orchestration_service import MasterOrchestrationService


class MasterOrchestratorService:
    def __init__(self, repo: MasterOrchestratorRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = MasterGraphOrchestrator(llm_service)
        self.orch_service = MasterOrchestrationService(repo)

    def process_command_center_query(self, db: Session, user_id: int, query: str) -> Dict[str, Any]:
        career_state = self.orch_service.get_command_center_dashboard(db, user_id)
        agent = self.graph_orchestrator.master_agent
        agent_resp = agent.process_command(query, career_state)

        event = MasterCareerEvent(
            user_id=user_id,
            event_type="COMMAND_CENTER_QUERY",
            source_module="module_15",
            payload_json={"query": query, "reply": agent_resp["reply"]}
        )
        self.repo.record_event(event)
        return agent_resp

    def get_next_best_action(self, db: Session, user_id: int) -> Dict[str, Any]:
        return self.orch_service.calculate_next_best_action(db, user_id)

    def get_command_center_dashboard(self, db: Session, user_id: int) -> Dict[str, Any]:
        return self.orch_service.get_command_center_dashboard(db, user_id)

    def create_master_plan(self, user_id: int, goal_title: str) -> MasterCareerPlan:
        return self.orch_service.decompose_and_create_master_plan(user_id, goal_title)

    def get_active_plan(self, user_id: int) -> Optional[MasterCareerPlan]:
        return self.repo.get_active_plan(user_id)

    def list_strategies(self, user_id: int) -> List[MasterCareerStrategy]:
        return self.repo.list_strategies(user_id)

    def approve_action(self, user_id: int, approval_id: int) -> Optional[MasterApprovalRecord]:
        return self.repo.update_approval_status(approval_id, user_id, "APPROVED")

    def reject_action(self, user_id: int, approval_id: int) -> Optional[MasterApprovalRecord]:
        return self.repo.update_approval_status(approval_id, user_id, "REJECTED")
