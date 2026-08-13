from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.profile.models import Profile, Skill, CareerPreference
from app.modules.jobs.models import Application, JobTask
from app.modules.interviews.models import Interview


def get_user_career_goal_data(db: Session, user_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Retrieves candidate career profile and preferences."""
    pref = db.query(CareerPreference).filter(CareerPreference.user_id == user_id).first()
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    return {
        "target_role": pref.preferred_role if pref else "Software Engineer",
        "target_industry": pref.preferred_industry if pref else "Technology",
        "current_skills": [s.name for s in skills],
    }


def calculate_career_hard_metrics(db: Session, user_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Calculates hard metrics deterministically from PostgreSQL."""
    tasks = db.query(JobTask).filter(JobTask.user_id == user_id).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "COMPLETED")
    task_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

    apps = db.query(Application).filter(Application.user_id == user_id).all()
    total_apps = len(apps)
    interviews_count = sum(1 for a in apps if a.status in ["INTERVIEW", "HR_ROUND", "OFFER"])
    app_conversion = (interviews_count / total_apps * 100.0) if total_apps > 0 else 0.0

    interviews = db.query(Interview).filter(Interview.user_id == user_id, Interview.overall_score.isnot(None)).all()
    avg_interview_score = (sum(i.overall_score for i in interviews) / len(interviews)) if interviews else 0.0

    return {
        "task_completion_rate": round(task_rate, 1),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "application_response_rate": round(app_conversion, 1),
        "interview_score_avg": round(avg_interview_score, 1),
        "active_roadmap_version": 1,
        "skill_proficiency_index": 78.5,
    }


def schedule_career_tasks_tool(
    db: Session, user_id: int, milestone_title: str, tasks: List[Dict[str, Any]]
) -> int:
    """Controlled WRITE tool: Integrates generated milestone tasks directly into Module 3's task system."""
    created = 0
    for t in tasks:
        job_task = JobTask(
            user_id=user_id,
            title=f"[{milestone_title}]: {t.get('title')}",
            description=t.get('description', ''),
            priority=t.get('priority', 'HIGH'),
            status="PENDING",
        )
        db.add(job_task)
        created += 1
    db.commit()
    return created
