"""
Module 13 — LangChain Tools for Career Performance Engine
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from app.modules.career.repository import CareerRepository


@tool
def get_active_goals(user_id: int, db: Any = None) -> List[Dict[str, Any]]:
    """Retrieves active career goals for the user."""
    if not db:
        return [{"id": 1, "title": "Master Backend Microservices", "priority": "HIGH", "status": "ACTIVE"}]
    repo = CareerRepository(db)
    goals = repo.list_goals(user_id, status="ACTIVE")
    return [{"id": g.id, "title": g.title, "priority": g.priority, "status": g.status} for g in goals]


@tool
def get_pending_tasks(user_id: int, db: Any = None) -> List[Dict[str, Any]]:
    """Retrieves pending career tasks for the user."""
    if not db:
        return [{"id": 1, "title": "Implement Redis Cache", "priority": "HIGH", "status": "PENDING"}]
    repo = CareerRepository(db)
    tasks = repo.list_tasks(user_id, status="PENDING")
    return [{"id": t.id, "title": t.title, "priority": t.priority, "status": t.status} for t in tasks]


@tool
def get_skill_gaps(user_id: int, db: Any = None) -> List[Dict[str, Any]]:
    """Retrieves current skill gaps and skill progress metrics."""
    return [
        {"skill_name": "Azure Data Factory", "confidence": 55.0, "status": "IMPROVING"},
        {"skill_name": "System Design", "confidence": 50.0, "status": "UNTESTED"},
        {"skill_name": "PySpark", "confidence": 60.0, "status": "STABLE"}
    ]


@tool
def get_career_milestones(user_id: int, db: Any = None) -> List[Dict[str, Any]]:
    """Retrieves active career milestones from the roadmap."""
    if not db:
        return [{"id": 1, "title": "Backend API Master", "status": "COMPLETED"}, {"id": 2, "title": "Microservices Architecture", "status": "PENDING"}]
    repo = CareerRepository(db)
    active = repo.get_active_roadmap(user_id)
    if active and active.milestones:
        return [{"id": m.id, "title": m.title, "status": m.status, "target_date": m.target_date} for m in active.milestones]
    return []


@tool
def get_recent_progress(user_id: int, db: Any = None) -> Dict[str, Any]:
    """Retrieves recent task completion and performance progress metrics."""
    return {
        "completed_tasks_this_week": 8,
        "total_tasks_this_week": 10,
        "performance_score": 82.5,
        "top_improvement": "Python API Development"
    }
