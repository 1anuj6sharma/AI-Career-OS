from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.profile.models import Profile, Skill, Experience, Education, CareerPreference


def get_user_profile_data(db: Session, user_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Retrieves user profile data from DB."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    experiences = db.query(Experience).filter(Experience.user_id == user_id).all()
    educations = db.query(Education).filter(Education.user_id == user_id).all()
    preference = db.query(CareerPreference).filter(CareerPreference.user_id == user_id).first()

    return {
        "full_name": profile.full_name if profile else "User",
        "current_role": profile.current_role if profile else None,
        "target_role": profile.target_role if profile else None,
        "years_of_experience": profile.years_of_experience if profile else 0,
        "work_preference": profile.work_preference if profile else "REMOTE",
        "skills": [s.name for s in skills],
        "experiences": [
            {
                "company": e.company,
                "role": e.role,
                "description": e.description,
                "technologies": e.technologies,
            }
            for e in experiences
        ],
        "educations": [
            {"degree": ed.degree, "institution": ed.institution, "field": ed.field_of_study}
            for ed in educations
        ],
        "target_roles": preference.target_roles if preference else [],
        "target_companies": preference.target_companies if preference else [],
    }
