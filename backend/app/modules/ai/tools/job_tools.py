from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.jobs.models import Job, Company
from app.modules.ai.tools.profile_tools import get_user_profile_data


def get_job_data(db: Session, user_id: int, job_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Retrieves job details for user."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    if not job:
        return {}

    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "description": job.description or "",
        "location": job.location,
        "remote_type": job.remote_type,
        "employment_type": job.employment_type,
        "experience_level": job.experience_level,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.currency,
        "is_favorite": job.is_favorite,
    }


def calculate_hybrid_job_match(
    db: Session, user_id: int, job_id: int
) -> Dict[str, Any]:
    """
    Deterministic Job Fit Score Calculation:
    - 40% Required Skills Match
    - 20% Experience Match
    - 15% Education Match
    - 10% Location / Remote Preference
    - 15% Career Goals / Target Role Match
    """
    profile = get_user_profile_data(db, user_id)
    job = get_job_data(db, user_id, job_id)

    if not job:
        return {"overall_score": 0, "evidence": "Job not found"}

    user_skills = set([s.lower() for s in profile.get("skills", [])])
    job_desc = job.get("description", "").lower()
    job_title = job.get("title", "").lower()

    # 1. Skill Score (40%)
    matched_skills = [s for s in user_skills if s in job_desc or s in job_title]
    skill_score = min(1.0, len(matched_skills) / max(len(user_skills), 1)) * 40.0

    # 2. Experience Score (20%)
    user_exp = profile.get("years_of_experience", 0)
    exp_score = 20.0 if user_exp >= 3 else (user_exp / 3.0) * 20.0

    # 3. Education Score (15%)
    edu_score = 15.0 if len(profile.get("educations", [])) > 0 else 7.5

    # 4. Preference Score (10%)
    user_pref = (profile.get("work_preference") or "REMOTE").upper()
    job_remote = (job.get("remote_type") or "REMOTE").upper()
    pref_score = 10.0 if user_pref == job_remote else 5.0

    # 5. Career Goal Score (15%)
    target_roles = [r.lower() for r in profile.get("target_roles", [])]
    goal_score = 15.0 if any(r in job_title for r in target_roles) or profile.get("target_role", "").lower() in job_title else 7.5

    overall_score = round(skill_score + exp_score + edu_score + pref_score + goal_score, 1)

    return {
        "job_id": job_id,
        "job_title": job["title"],
        "company_name": job["company_name"],
        "overall_score": overall_score,
        "breakdown": {
            "skill_score": round(skill_score, 1),
            "experience_score": round(exp_score, 1),
            "education_score": round(edu_score, 1),
            "preference_score": round(pref_score, 1),
            "goal_score": round(goal_score, 1),
        },
        "matched_skills": matched_skills,
        "user_skills_total": len(user_skills),
    }
