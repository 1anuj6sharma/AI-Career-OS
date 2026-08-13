from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.ai.services.llm_service import LLMService
from app.modules.ai.graph.career_graph import CareerGraphOrchestrator
from app.modules.ai.agents import (
    CareerStrategistAgent,
    JobMatchAgent,
    InterviewAgent,
    PlannerAgent,
)
from app.modules.ai.models import AIConversation, AIMessage, AIPendingAction, AIRun
from app.modules.ai.schemas import (
    AIChatRequest,
    AIChatResponse,
    PendingActionOut,
    PendingActionApproveRequest,
    AIRunOut,
)
from app.modules.ai.services.observability_service import start_ai_run, finish_ai_run
from app.modules.ai.memory.short_term import add_message_to_conversation

router = APIRouter(prefix="/ai", tags=["Module 4 — AI Career Intelligence"])

llm_service = LLMService()
graph_orchestrator = CareerGraphOrchestrator(llm_service)


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Multi-turn AI Copilot chat via LangGraph orchestrator",
)
def chat_copilot(
    data: AIChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # 1. Get or create conversation
    conv = None
    if data.conversation_id:
        conv = db.query(AIConversation).filter(AIConversation.id == data.conversation_id, AIConversation.user_id == current_user.id).first()

    if not conv:
        conv = AIConversation(user_id=current_user.id, title="Career Copilot Session")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Save user message
    add_message_to_conversation(db, conv.id, "user", data.message)

    # 2. Start AI Run Observability
    run_log = start_ai_run(db, current_user.id, "langgraph_chat")

    try:
        # 3. Execute LangGraph workflow
        result = graph_orchestrator.run(
            db=db,
            user_id=current_user.id,
            user_request=data.message,
            job_id=data.job_id,
        )

        reply_text = result.get("final_response", "AI analysis complete.")

        # Save assistant message
        add_message_to_conversation(db, conv.id, "assistant", reply_text)

        finish_ai_run(db, run_log.id, "COMPLETED", tokens_used=150)

        return AIChatResponse(
            conversation_id=conv.id,
            intent=result.get("intent", "career"),
            reply=reply_text,
            agent_results=result.get("agent_results"),
            pending_actions=result.get("pending_actions"),
        )
    except Exception as e:
        finish_ai_run(db, run_log.id, "FAILED", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/career/analyze",
    summary="Analyze profile and pipeline via Career Strategist Agent",
)
def analyze_career(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    agent = CareerStrategistAgent(llm_service)
    return agent.run(db, current_user.id)


@router.post(
    "/jobs/{job_id}/match",
    summary="Compute hybrid deterministic + LLM match score for job",
)
def match_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    agent = JobMatchAgent(llm_service)
    return agent.run(db, current_user.id, job_id)


@router.post(
    "/jobs/{job_id}/prepare",
    summary="Generate technical & behavioral interview kit for job",
)
def prepare_interview(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    agent = InterviewAgent(llm_service)
    return agent.run(db, current_user.id, job_id)


@router.post(
    "/career/plan",
    summary="Synthesize daily plan and schedule follow-up tasks",
)
def plan_career(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    agent = PlannerAgent(llm_service)
    return agent.run(db, current_user.id)


# ================= HUMAN IN THE LOOP =================

@router.get(
    "/pending-actions",
    response_model=List[PendingActionOut],
    summary="Get pending AI actions requiring human approval",
)
def get_pending_actions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(AIPendingAction)
        .filter(AIPendingAction.user_id == current_user.id, AIPendingAction.is_executed == False)
        .order_by(AIPendingAction.created_at.desc())
        .all()
    )


@router.post(
    "/pending-actions/{action_id}/approve",
    summary="Human Approval endpoint for sensitive AI actions",
)
def approve_pending_action(
    action_id: int,
    data: PendingActionApproveRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    action = (
        db.query(AIPendingAction)
        .filter(AIPendingAction.id == action_id, AIPendingAction.user_id == current_user.id)
        .first()
    )
    if not action:
        raise HTTPException(status_code=404, detail="Pending action not found")

    action.is_approved = data.approve
    action.is_executed = True
    db.commit()

    return {"action_id": action_id, "approved": data.approve, "status": "PROCESSED"}


# ================= OBSERVABILITY =================

@router.get(
    "/runs",
    response_model=List[AIRunOut],
    summary="List AI agentic execution run logs and metrics",
)
def list_ai_runs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(AIRun)
        .filter(AIRun.user_id == current_user.id)
        .order_by(AIRun.started_at.desc())
        .limit(20)
        .all()
    )
