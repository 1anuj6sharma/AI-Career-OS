import json
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.models.profile import Profile, Skill
from app.models.jobs import SavedJob, JobApplication
from app.models.resumes import Resume
from app.models.ai_coach import CareerMemory
from app.models.career import CareerTask

# Note: In a production LangGraph setup, tools need access to the DB.
# For simplicity in this functional design, we will define them and pass DB implicitly or via context.

@tool
def get_user_profile(user_id: int, db: Session) -> str:
    """Retrieve the core career profile for the user, including target role and summary."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return "No profile found. Advise user to set up their career profile."
    
    return json.dumps({
        "name": profile.name,
        "target_role": profile.target_role,
        "years_experience": profile.years_experience,
        "current_role": profile.current_role
    })

@tool
def get_user_skills(user_id: int, db: Session) -> str:
    """Retrieve all validated skills the user possesses."""
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    if not skills:
        return "No skills found. Advise user to add skills to their profile."
    
    skill_names = [s.name for s in skills]
    return f"User skills: {', '.join(skill_names)}"

@tool
def get_recent_job_applications(user_id: int, db: Session) -> str:
    """Retrieve recent job applications to analyze conversion rates."""
    apps = db.query(JobApplication).filter(JobApplication.user_id == user_id).limit(10).all()
    if not apps:
        return "No recent job applications."
    
    data = [{"company": a.company, "status": a.status, "date": str(a.applied_date)} for a in apps]
    return json.dumps(data)

@tool
def create_career_task(user_id: int, title: str, priority: str, estimated_minutes: int, db: Session) -> str:
    """Create an actionable career task for the user (e.g. 'Practice System Design', 'Update Resume')."""
    task = CareerTask(
        user_id=user_id,
        title=title,
        priority=priority,
        estimated_minutes=estimated_minutes
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return f"Task created successfully with ID {task.id}"

@tool
def save_career_memory(user_id: int, memory_type: str, content: str, db: Session) -> str:
    """Save an important insight or preference about the user into long-term memory."""
    mem = CareerMemory(
        user_id=user_id,
        memory_type=memory_type,
        content=content
    )
    db.add(mem)
    db.commit()
    return "Memory saved successfully."
