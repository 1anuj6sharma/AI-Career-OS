from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.modules.master_orchestrator.models import (
    MasterCareerPlan,
    MasterPlanStep,
    MasterCareerDecision,
    MasterCareerEvent,
    MasterCareerMemory,
    MasterCareerStrategy,
    MasterApprovalRecord,
)


class MasterOrchestratorRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------------
    # Master Plans & Steps
    # ------------------------------------------------------------------------
    def create_plan(self, plan: MasterCareerPlan) -> MasterCareerPlan:
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_active_plan(self, user_id: int) -> Optional[MasterCareerPlan]:
        return (
            self.db.query(MasterCareerPlan)
            .options(joinedload(MasterCareerPlan.steps))
            .filter(MasterCareerPlan.user_id == user_id, MasterCareerPlan.status == "ACTIVE")
            .order_by(MasterCareerPlan.version.desc())
            .first()
        )

    def create_plan_step(self, step: MasterPlanStep) -> MasterPlanStep:
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    # ------------------------------------------------------------------------
    # Master Decisions & Events
    # ------------------------------------------------------------------------
    def create_decision(self, decision: MasterCareerDecision) -> MasterCareerDecision:
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        return decision

    def record_event(self, event: MasterCareerEvent) -> MasterCareerEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(self, user_id: int, limit: int = 20) -> List[MasterCareerEvent]:
        return (
            self.db.query(MasterCareerEvent)
            .filter(MasterCareerEvent.user_id == user_id)
            .order_by(MasterCareerEvent.created_at.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------------
    # 3-Level Career Memory
    # ------------------------------------------------------------------------
    def save_memory(self, memory: MasterCareerMemory) -> MasterCareerMemory:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_memories(self, user_id: int, memory_type: Optional[str] = None) -> List[MasterCareerMemory]:
        query = self.db.query(MasterCareerMemory).filter(MasterCareerMemory.user_id == user_id)
        if memory_type:
            query = query.filter(MasterCareerMemory.memory_type == memory_type)
        return query.order_by(MasterCareerMemory.created_at.desc()).all()

    # ------------------------------------------------------------------------
    # Adaptive Strategies
    # ------------------------------------------------------------------------
    def get_active_strategy(self, user_id: int) -> Optional[MasterCareerStrategy]:
        return (
            self.db.query(MasterCareerStrategy)
            .filter(MasterCareerStrategy.user_id == user_id, MasterCareerStrategy.is_active == True)
            .order_by(MasterCareerStrategy.version_number.desc())
            .first()
        )

    def archive_old_strategies(self, user_id: int) -> None:
        self.db.query(MasterCareerStrategy).filter(
            MasterCareerStrategy.user_id == user_id, MasterCareerStrategy.is_active == True
        ).update({"is_active": False})
        self.db.commit()

    def create_strategy(self, strategy: MasterCareerStrategy) -> MasterCareerStrategy:
        self.archive_old_strategies(strategy.user_id)
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def list_strategies(self, user_id: int) -> List[MasterCareerStrategy]:
        return (
            self.db.query(MasterCareerStrategy)
            .filter(MasterCareerStrategy.user_id == user_id)
            .order_by(MasterCareerStrategy.version_number.desc())
            .all()
        )

    # ------------------------------------------------------------------------
    # Approvals Gateway
    # ------------------------------------------------------------------------
    def create_approval(self, approval: MasterApprovalRecord) -> MasterApprovalRecord:
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def list_pending_approvals(self, user_id: int) -> List[MasterApprovalRecord]:
        return (
            self.db.query(MasterApprovalRecord)
            .filter(MasterApprovalRecord.user_id == user_id, MasterApprovalRecord.status == "PENDING_APPROVAL")
            .order_by(MasterApprovalRecord.created_at.desc())
            .all()
        )

    def update_approval_status(self, approval_id: int, user_id: int, status: str) -> Optional[MasterApprovalRecord]:
        app = (
            self.db.query(MasterApprovalRecord)
            .filter(MasterApprovalRecord.id == approval_id, MasterApprovalRecord.user_id == user_id)
            .first()
        )
        if app:
            app.status = status
            if status == "APPROVED":
                app.approved_at = datetime.now()
            self.db.commit()
            self.db.refresh(app)
        return app
