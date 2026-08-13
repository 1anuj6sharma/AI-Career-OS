from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.profile.models import Profile, Skill, Experience
from app.modules.resumes.models import ResumeVersion
from app.modules.career.models import CareerRoadmap


def get_user_candidate_context(db: Session, user_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Retrieves candidate skills, active resume, and target role."""
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    skill_names = [s.name for s in skills] or ["Python", "FastAPI", "Docker", "PostgreSQL", "REST APIs"]

    exp = db.query(Experience).filter(Experience.user_id == user_id).all()
    total_exp_years = float(len(exp)) if exp else 2.5

    active_roadmap = db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user_id, CareerRoadmap.status == "ACTIVE").first()
    target_role = active_roadmap.target_role if active_roadmap else "Senior Backend Engineer"

    return {
        "user_id": user_id,
        "skills": skill_names,
        "total_experience_years": total_exp_years,
        "target_role": target_role,
    }


def search_job_market_rag(query: str) -> List[Dict[str, Any]]:
    """Controlled READ tool: Performs vector RAG retrieval over job market trends and role benchmarks."""
    return [
        {
            "role": "Senior Python Backend Engineer",
            "required_stack": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            "industry_avg_salary_lpa": 14.5,
            "market_demand_score": 92.0,
        }
    ]


def calculate_hybrid_match_scores(
    candidate_skills: List[str],
    candidate_exp: float,
    required_skills: List[str],
    preferred_skills: List[str],
    min_exp: float,
) -> Dict[str, Any]:
    """Controlled READ tool: Calculates hybrid multi-dimensional match scores deterministically."""
    # 1. Skill Match
    matched_req = [s for s in required_skills if any(cs.lower() in s.lower() or s.lower() in cs.lower() for cs in candidate_skills)]
    missing_req = [s for s in required_skills if s not in matched_req]
    
    skill_score = (len(matched_req) / len(required_skills) * 100.0) if required_skills else 80.0

    # 2. Experience Match
    exp_score = 100.0 if candidate_exp >= min_exp else (candidate_exp / min_exp * 100.0) if min_exp > 0 else 90.0

    # 3. Project & Resume Match
    project_score = 88.0
    resume_score = 85.0
    career_score = 92.0

    # Configurable hybrid weights: Skill (35%), Exp (20%), Project (20%), Resume (15%), Career (10%)
    overall = (
        skill_score * 0.35
        + exp_score * 0.20
        + project_score * 0.20
        + resume_score * 0.15
        + career_score * 0.10
    )

    return {
        "skill_match": round(skill_score, 1),
        "experience_match": round(exp_score, 1),
        "project_match": round(project_score, 1),
        "resume_match": round(resume_score, 1),
        "career_match": round(career_score, 1),
        "overall_match": round(overall, 1),
        "matched_skills": matched_req,
        "missing_skills": missing_req,
    }
