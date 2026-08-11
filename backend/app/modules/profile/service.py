from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.modules.profile.models import Profile, Skill, Education, Experience, Certification, CareerPreference
from app.modules.profile.repository import (
    ProfileRepository, SkillRepository, EducationRepository,
    ExperienceRepository, CertificationRepository, CareerPreferenceRepository
)
from app.modules.profile.schemas import (
    ProfileUpdate, SkillCreate, SkillUpdate, EducationCreate, EducationUpdate,
    ExperienceCreate, ExperienceUpdate, CertificationCreate, CertificationUpdate,
    CareerPreferenceUpdate, FullProfileResponse
)

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.skill_repo = SkillRepository(db)
        self.education_repo = EducationRepository(db)
        self.experience_repo = ExperienceRepository(db)
        self.cert_repo = CertificationRepository(db)
        self.pref_repo = CareerPreferenceRepository(db)

    def _ensure_profile_exists(self, user_id: int) -> Profile:
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = self.profile_repo.create(Profile(user_id=user_id))
            self.db.commit()
        return profile

    def get_full_profile(self, user_id: int) -> FullProfileResponse:
        profile = self._ensure_profile_exists(user_id)
        skills = self.skill_repo.get_all_by_user(user_id)
        education = self.education_repo.get_all_by_user(user_id)
        experience = self.experience_repo.get_all_by_user(user_id)
        certifications = self.cert_repo.get_all_by_user(user_id)
        preferences = self.pref_repo.get_by_user_id(user_id)
        
        return FullProfileResponse(
            profile=profile,
            skills=skills,
            education=education,
            experience=experience,
            certifications=certifications,
            career_preferences=preferences
        )

    def update_profile(self, user_id: int, update_data: ProfileUpdate, partial: bool = False) -> Profile:
        profile = self._ensure_profile_exists(user_id)
        update_dict = update_data.model_dump(exclude_unset=partial)
        
        for key, value in update_dict.items():
            setattr(profile, key, value)
            
        profile = self.profile_repo.update(profile)
        self.db.commit()
        return profile

    # --- Skills ---
    def get_skills(self, user_id: int) -> List[Skill]:
        return self.skill_repo.get_all_by_user(user_id)

    def add_skill(self, user_id: int, data: SkillCreate) -> Skill:
        skill = Skill(user_id=user_id, **data.model_dump())
        skill = self.skill_repo.create(skill)
        self.db.commit()
        return skill

    def update_skill(self, user_id: int, skill_id: int, data: SkillUpdate) -> Skill:
        skill = self.skill_repo.get_by_id_and_user(skill_id, user_id)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
            
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(skill, key, value)
            
        skill = self.skill_repo.update(skill)
        self.db.commit()
        return skill

    def delete_skill(self, user_id: int, skill_id: int) -> None:
        skill = self.skill_repo.get_by_id_and_user(skill_id, user_id)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        self.skill_repo.delete(skill)
        self.db.commit()

    # --- Education ---
    def get_education(self, user_id: int) -> List[Education]:
        return self.education_repo.get_all_by_user(user_id)

    def add_education(self, user_id: int, data: EducationCreate) -> Education:
        edu = Education(user_id=user_id, **data.model_dump())
        edu = self.education_repo.create(edu)
        self.db.commit()
        return edu

    def update_education(self, user_id: int, education_id: int, data: EducationUpdate) -> Education:
        edu = self.education_repo.get_by_id_and_user(education_id, user_id)
        if not edu:
            raise HTTPException(status_code=404, detail="Education record not found")
            
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(edu, key, value)
            
        edu = self.education_repo.update(edu)
        self.db.commit()
        return edu

    def delete_education(self, user_id: int, education_id: int) -> None:
        edu = self.education_repo.get_by_id_and_user(education_id, user_id)
        if not edu:
            raise HTTPException(status_code=404, detail="Education record not found")
        self.education_repo.delete(edu)
        self.db.commit()

    # --- Experience ---
    def get_experience(self, user_id: int) -> List[Experience]:
        return self.experience_repo.get_all_by_user(user_id)

    def add_experience(self, user_id: int, data: ExperienceCreate) -> Experience:
        exp = Experience(user_id=user_id, **data.model_dump())
        exp = self.experience_repo.create(exp)
        self.db.commit()
        return exp

    def update_experience(self, user_id: int, experience_id: int, data: ExperienceUpdate) -> Experience:
        exp = self.experience_repo.get_by_id_and_user(experience_id, user_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Experience record not found")
            
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(exp, key, value)
            
        exp = self.experience_repo.update(exp)
        self.db.commit()
        return exp

    def delete_experience(self, user_id: int, experience_id: int) -> None:
        exp = self.experience_repo.get_by_id_and_user(experience_id, user_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Experience record not found")
        self.experience_repo.delete(exp)
        self.db.commit()

    # --- Certifications ---
    def get_certifications(self, user_id: int) -> List[Certification]:
        return self.cert_repo.get_all_by_user(user_id)

    def add_certification(self, user_id: int, data: CertificationCreate) -> Certification:
        cert = Certification(user_id=user_id, **data.model_dump())
        cert = self.cert_repo.create(cert)
        self.db.commit()
        return cert

    def update_certification(self, user_id: int, certification_id: int, data: CertificationUpdate) -> Certification:
        cert = self.cert_repo.get_by_id_and_user(certification_id, user_id)
        if not cert:
            raise HTTPException(status_code=404, detail="Certification not found")
            
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(cert, key, value)
            
        cert = self.cert_repo.update(cert)
        self.db.commit()
        return cert

    def delete_certification(self, user_id: int, certification_id: int) -> None:
        cert = self.cert_repo.get_by_id_and_user(certification_id, user_id)
        if not cert:
            raise HTTPException(status_code=404, detail="Certification not found")
        self.cert_repo.delete(cert)
        self.db.commit()

    # --- Career Preferences ---
    def get_career_preferences(self, user_id: int) -> Optional[CareerPreference]:
        return self.pref_repo.get_by_user_id(user_id)

    def update_career_preferences(self, user_id: int, data: CareerPreferenceUpdate) -> CareerPreference:
        pref = self.pref_repo.get_by_user_id(user_id)
        if not pref:
            pref = CareerPreference(user_id=user_id)
            self.pref_repo.create(pref)
            
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(pref, key, value)
            
        pref = self.pref_repo.update(pref)
        self.db.commit()
        return pref
