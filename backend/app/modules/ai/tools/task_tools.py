from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.jobs.models import JobTask, Application


def create_ai_task_tool(
    db: Session, user_id: int, application_id: int, title: str, description: str = None, priority: str = "HIGH"
) -> Dict[str, Any]:
    """Controlled WRITE tool: Creates a task for an application."""
    app = db.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
    if not app:
        return {"error": "Application not found"}

    task = JobTask(
        user_id=user_id,
        application_id=application_id,
        title=title,
        description=description,
        priority=priority,
        status="PENDING",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
    }
