from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.jobs.models import Application
from app.modules.ai.models import AIPendingAction


def get_active_applications_data(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Controlled READ tool: Retrieves user's active applications."""
    apps = (
        db.query(Application)
        .filter(Application.user_id == user_id)
        .order_by(Application.updated_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
            "notes": a.notes,
        }
        for a in apps
    ]


def request_application_status_update(
    db: Session, user_id: int, application_id: int, new_status: str, run_id: int = None
) -> Dict[str, Any]:
    """
    HIGH-RISK WRITE tool with Human-In-The-Loop.
    Creates a pending action for user approval before mutating database status.
    """
    pending = AIPendingAction(
        user_id=user_id,
        run_id=run_id,
        action_type="UPDATE_APPLICATION_STATUS",
        description=f"Request to change application status to {new_status}",
        payload={"application_id": application_id, "new_status": new_status},
        is_approved=False,
        is_executed=False,
    )
    db.add(pending)
    db.commit()
    db.refresh(pending)

    return {
        "status": "APPROVAL_REQUIRED",
        "pending_action_id": pending.id,
        "description": pending.description,
        "message": "Status change submitted for user review & approval.",
    }
