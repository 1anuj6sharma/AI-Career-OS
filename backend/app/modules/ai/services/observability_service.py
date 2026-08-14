from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.ai.models import AIRun, AIToolCall


def start_ai_run(db: Session, user_id: int, workflow_name: str, model: str = "gemini-1.5-flash") -> AIRun:
    run = AIRun(
        user_id=user_id,
        workflow_name=workflow_name,
        status="RUNNING",
        model=model,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_ai_run(db: Session, run_id: int, status: str = "COMPLETED", tokens_used: int = 0, error: str = None) -> AIRun:
    run = db.query(AIRun).filter(AIRun.id == run_id).first()
    if run:
        run.status = status
        run.completed_at = datetime.now()
        run.tokens_used = tokens_used
        run.error = error
        db.commit()
        db.refresh(run)
    return run


def log_tool_call(db: Session, run_id: int, tool_name: str, input_params: Dict[str, Any], output_result: Dict[str, Any], status: str = "SUCCESS") -> AIToolCall:
    tool_call = AIToolCall(
        run_id=run_id,
        tool_name=tool_name,
        input_params=input_params,
        output_result=output_result,
        status=status,
    )
    db.add(tool_call)
    db.commit()
    db.refresh(tool_call)
    return tool_call
