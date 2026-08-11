from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.profile.service import ProfileService
from app.modules.profile.schemas import (
    FullProfileResponse, ProfileResponse, ProfileUpdate,
    SkillResponse, SkillCreate, SkillUpdate,
    EducationResponse, EducationCreate, EducationUpdate,
    ExperienceResponse, ExperienceCreate, ExperienceUpdate,
    CertificationResponse, CertificationCreate, CertificationUpdate,
    CareerPreferenceResponse, CareerPreferenceUpdate, MessageResponse
)

router = APIRouter(prefix="/profile", tags=["Profile"])

def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


# --- Profile ---

@router.get("", response_model=FullProfileResponse, summary="Get full profile")
def get_full_profile(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    """Get the complete profile for the authenticated user. Automatically creates a base profile if it doesn't exist."""
    return service.get_full_profile(current_user.id)

@router.put("", response_model=ProfileResponse, summary="Update profile (full)")
def update_profile_full(
    data: ProfileUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    """Full update of the user's base profile."""
    return service.update_profile(current_user.id, data, partial=False)

@router.patch("", response_model=ProfileResponse, summary="Update profile (partial)")
def update_profile_partial(
    data: ProfileUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    """Partial update of the user's base profile."""
    return service.update_profile(current_user.id, data, partial=True)


# --- Skills ---

@router.get("/skills", response_model=List[SkillResponse], summary="Get skills")
def get_skills(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.get_skills(current_user.id)

@router.post("/skills", response_model=SkillResponse, summary="Add a skill", status_code=status.HTTP_201_CREATED)
def add_skill(
    data: SkillCreate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.add_skill(current_user.id, data)

@router.put("/skills/{skill_id}", response_model=SkillResponse, summary="Update a skill")
def update_skill(
    skill_id: int,
    data: SkillUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.update_skill(current_user.id, skill_id, data)

@router.delete("/skills/{skill_id}", response_model=MessageResponse, summary="Delete a skill")
def delete_skill(
    skill_id: int,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    service.delete_skill(current_user.id, skill_id)
    return MessageResponse(message="Skill deleted successfully")


# --- Education ---

@router.get("/education", response_model=List[EducationResponse], summary="Get education records")
def get_education(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.get_education(current_user.id)

@router.post("/education", response_model=EducationResponse, summary="Add an education record", status_code=status.HTTP_201_CREATED)
def add_education(
    data: EducationCreate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.add_education(current_user.id, data)

@router.put("/education/{education_id}", response_model=EducationResponse, summary="Update an education record")
def update_education(
    education_id: int,
    data: EducationUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.update_education(current_user.id, education_id, data)

@router.delete("/education/{education_id}", response_model=MessageResponse, summary="Delete an education record")
def delete_education(
    education_id: int,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    service.delete_education(current_user.id, education_id)
    return MessageResponse(message="Education record deleted successfully")


# --- Experience ---

@router.get("/experience", response_model=List[ExperienceResponse], summary="Get experience records")
def get_experience(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.get_experience(current_user.id)

@router.post("/experience", response_model=ExperienceResponse, summary="Add an experience record", status_code=status.HTTP_201_CREATED)
def add_experience(
    data: ExperienceCreate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.add_experience(current_user.id, data)

@router.put("/experience/{experience_id}", response_model=ExperienceResponse, summary="Update an experience record")
def update_experience(
    experience_id: int,
    data: ExperienceUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.update_experience(current_user.id, experience_id, data)

@router.delete("/experience/{experience_id}", response_model=MessageResponse, summary="Delete an experience record")
def delete_experience(
    experience_id: int,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    service.delete_experience(current_user.id, experience_id)
    return MessageResponse(message="Experience record deleted successfully")


# --- Certifications ---

@router.get("/certifications", response_model=List[CertificationResponse], summary="Get certifications")
def get_certifications(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.get_certifications(current_user.id)

@router.post("/certifications", response_model=CertificationResponse, summary="Add a certification", status_code=status.HTTP_201_CREATED)
def add_certification(
    data: CertificationCreate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.add_certification(current_user.id, data)

@router.put("/certifications/{certification_id}", response_model=CertificationResponse, summary="Update a certification")
def update_certification(
    certification_id: int,
    data: CertificationUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.update_certification(current_user.id, certification_id, data)

@router.delete("/certifications/{certification_id}", response_model=MessageResponse, summary="Delete a certification")
def delete_certification(
    certification_id: int,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    service.delete_certification(current_user.id, certification_id)
    return MessageResponse(message="Certification deleted successfully")


# --- Career Preferences ---

@router.get("/career-preferences", response_model=CareerPreferenceResponse, summary="Get career preferences")
def get_career_preferences(
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    prefs = service.get_career_preferences(current_user.id)
    if not prefs:
        prefs = service.update_career_preferences(current_user.id, CareerPreferenceUpdate())
    return prefs

@router.put("/career-preferences", response_model=CareerPreferenceResponse, summary="Update career preferences")
def update_career_preferences(
    data: CareerPreferenceUpdate,
    current_user = Depends(get_current_active_user),
    service: ProfileService = Depends(get_profile_service)
):
    return service.update_career_preferences(current_user.id, data)
