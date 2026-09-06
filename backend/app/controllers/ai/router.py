from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.controllers.auth.dependencies import get_current_active_user
from app.models.auth import User
from app.controllers.ai.services.llm_service import LLMService
from app.controllers.ai.graph.career_graph import CareerGraphOrchestrator
from app.controllers.ai.agents import (
    CareerStrategistAgent,
    JobMatchAgent,
    InterviewAgent,
    PlannerAgent,
)
from app.models.ai import AIConversation, AIMessage, AIPendingAction, AIRun
from app.views.ai import (
    AIChatRequest,
    AIChatResponse,
    PendingActionOut,
    PendingActionApproveRequest,
    AIRunOut,
)
from app.controllers.ai.services.observability_service import start_ai_run, finish_ai_run
from app.controllers.ai.memory.short_term import add_message_to_conversation
from app.models.ai_coach import CareerHealthScore
from app.models.career import CareerTask, CareerRoadmap

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

@router.get(
    "/coach/health",
    summary="Get the dynamic Career Health Score",
)
def get_career_health(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Retrieve the latest calculated score, or create a mock/baseline one if none exists
    score = db.query(CareerHealthScore).filter(CareerHealthScore.user_id == current_user.id).order_by(CareerHealthScore.calculated_at.desc()).first()
    if not score:
        # Provide a default baseline score
        score = CareerHealthScore(
            user_id=current_user.id,
            total_score=78,
            skills_score=82,
            resume_score=74,
            portfolio_score=68,
            interview_score=81,
            market_alignment_score=79,
            networking_score=61
        )
        db.add(score)
        db.commit()
        db.refresh(score)
        
    return {
        "total_score": score.total_score,
        "metrics": {
            "Skills": score.skills_score,
            "Resume": score.resume_score,
            "Portfolio": score.portfolio_score,
            "Interview": score.interview_score,
            "Market Alignment": score.market_alignment_score,
            "Networking": score.networking_score
        }
    }

@router.get(
    "/coach/brief",
    summary="Get Today's Career Plan / Brief",
)
def get_career_brief(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    tasks = db.query(CareerTask).filter(CareerTask.user_id == current_user.id, CareerTask.status == "pending").limit(3).all()
    
    if not tasks:
        # Fallback to planner agent if no explicitly saved tasks
        agent = PlannerAgent(llm_service)
        res = agent.run(db, current_user.id)
        return {"plan": res.get("daily_plan"), "tasks": []}

    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "impact": "Medium", # Fallback since career_tasks in career.py does not have impact field
                "estimated_minutes": t.estimated_minutes,
                "reason": t.description
            } for t in tasks
        ]
    }

@router.get(
    "/coach/gap-analysis",
    summary="Get Career Gap Analysis",
)
def get_gap_analysis(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Directly invoke the SkillGapAgent on the user's primary target
    agent = SkillGapAgent(llm_service)
    # job_id = None defaults to general profile gap
    res = agent.run(db, current_user.id, None)
    return {"analysis": res.get("analysis")}


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
