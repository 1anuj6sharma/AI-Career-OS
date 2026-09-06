from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List

from app.models.dashboard import ExecutionPlan, ApprovalQueue, CareerMemory
from app.views.dashboard import DashboardSummaryResponse, CareerHealthScore, OpportunityMatch, AgentTelemetry

from app.controllers.ai.services.llm_service import LLMService

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()

    def get_career_health(self, user_id: int) -> CareerHealthScore:
        # In a fully integrated system, this would calculate scores dynamically based on the DB state of skills, projects, and interviews.
        # For now, we simulate this as requested by the plan.
        return CareerHealthScore(
            score=78,
            goal_progress=64,
            readiness=72,
            opportunity_fit=86,
            execution=60,
            bottleneck="LangGraph Production Evidence",
            ai_priority="Build 1 production-grade agent workflow"
        )

    def get_opportunities(self, user_id: int) -> List[OpportunityMatch]:
        # Returns simulated matched opportunities based on User's career state
        return [
            OpportunityMatch(
                title="Senior ML Engineer",
                company="Anthropic • San Francisco (Hybrid)",
                match_score=91,
                verified_skills=["Python", "FastAPI"],
                missing_skills=["LangGraph"],
                recommendation="High Probability"
            ),
            OpportunityMatch(
                title="Agentic AI Workflows",
                company="Upwork Contract • $4,500 Budget",
                match_score=88,
                verified_skills=["FastAPI", "API Design"],
                missing_skills=[],
                recommendation="Easy Win"
            )
        ]

    def get_agent_telemetry(self) -> List[AgentTelemetry]:
        return [
            AgentTelemetry(agent_name="Opportunity Agent", status="Active", last_event="Scanned 126 new roles.", timestamp="Just now"),
            AgentTelemetry(agent_name="Matching Agent", status="Active", last_event="Ranked top 18 fits for Senior ML.", timestamp="2m ago"),
            AgentTelemetry(agent_name="Master Orchestrator", status="Active", last_event="Calibrated closed-loop plan.", timestamp="1h ago")
        ]

    def record_memory(self, user_id: int, event_type: str, description: str, source: str = "Dashboard"):
        memory = CareerMemory(
            user_id=user_id,
            event_type=event_type,
            description=description,
            source=source
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_summary(self, user_id: int) -> DashboardSummaryResponse:
        execution_plan = self.db.query(ExecutionPlan).filter(ExecutionPlan.user_id == user_id, ExecutionPlan.status.in_(["PENDING", "READY"])).all()
        
        # Seed initial data if empty for demo purposes
        if not execution_plan:
            plan = ExecutionPlan(user_id=user_id, action="Build LangGraph Agent", reason="Solves critical bottleneck", priority=1, status="READY", expected_impact="High")
            self.db.add(plan)
            self.db.commit()
            execution_plan = [plan]

        approvals = self.db.query(ApprovalQueue).filter(ApprovalQueue.user_id == user_id, ApprovalQueue.status == "PENDING").all()
        
        if not approvals:
            approval = ApprovalQueue(user_id=user_id, action_type="APPLY", title="Apply to Anthropic", description="Custom tailored resume ready for Senior AI Engineer role.", status="PENDING")
            self.db.add(approval)
            self.db.commit()
            approvals = [approval]

        memory = self.db.query(CareerMemory).filter(CareerMemory.user_id == user_id).order_by(CareerMemory.timestamp.desc()).limit(5).all()

        return DashboardSummaryResponse(
            career_health=self.get_career_health(user_id),
            execution_plan=execution_plan,
            approvals=approvals,
            opportunities=self.get_opportunities(user_id),
            agent_activity=self.get_agent_telemetry(),
            career_memory=memory
        )

    def complete_action(self, action_id: int, user_id: int):
        action = self.db.query(ExecutionPlan).filter(ExecutionPlan.id == action_id, ExecutionPlan.user_id == user_id).first()
        if action:
            action.status = "COMPLETED"
            action.completed_at = datetime.utcnow()
            self.db.commit()
            self.record_memory(user_id, "ACTION_COMPLETED", f"Completed action: {action.action}")
            return True
        return False

    def skip_action(self, action_id: int, user_id: int):
        action = self.db.query(ExecutionPlan).filter(ExecutionPlan.id == action_id, ExecutionPlan.user_id == user_id).first()
        if action:
            action.status = "SKIPPED"
            self.db.commit()
            self.record_memory(user_id, "ACTION_SKIPPED", f"Skipped action: {action.action}. Triggering AI re-evaluation.")
            # Here we would trigger LangGraph to adapt the strategy
            return True
        return False

    def generate_next_action(self, user_id: int) -> Dict[str, Any]:
        """
        Uses LangGraph/LLM to generate the next highest ROI action based on Career State.
        """
        prompt = f"Analyze the career state for user {user_id}. The bottleneck is 'LangGraph Production Evidence'. Suggest the highest ROI next action to unblock this."
        
        # Call LLM via LLMService
        result = self.llm_service.generate_json(prompt, schema={
            "action": "string",
            "reason": "string",
            "priority": "integer",
            "expected_impact": "string",
            "estimated_effort": "string",
            "confidence": "integer"
        })

        if result:
            # Persist the action
            new_plan = ExecutionPlan(
                user_id=user_id,
                action=result.get("action", "Unknown Action"),
                reason=result.get("reason", "No reason provided"),
                priority=result.get("priority", 1),
                status="READY",
                expected_impact=result.get("expected_impact", "Medium")
            )
            self.db.add(new_plan)
            self.record_memory(user_id, "AI_RECOMMENDATION_CREATED", f"AI recommended: {new_plan.action}")
            self.db.commit()
            self.db.refresh(new_plan)
            return result
        
        return {"error": "Failed to generate next action"}
